
import re
from typing import Literal

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

from app.graph.state import RouterState
from app.graph.billing import billing_agent_node
from app.graph.accounts import accounts_agent_node
from app.graph.support import support_agent_node
from app.graph.refund_approval import build_refund_approval_graph
from app.models.factory import get_llm

from app.tools.billing import (
    get_invoice,
    get_payment,
    get_transactions_by_customer_id,
)


def extract_identifiers(state: RouterState) -> dict:
    """Extract identifiers and a basic refund reason from the request."""
    question = state.get("question", "")

    result = {}

    customer_match = re.search(
        r"\bCUST-\d+\b", question, re.IGNORECASE
    )
    invoice_match = re.search(
        r"\bINV-\d+\b", question, re.IGNORECASE
    )

    if customer_match and not state.get("customer_id"):
        result["customer_id"] = customer_match.group(0).upper()

    if invoice_match and not state.get("invoice_id"):
        result["invoice_id"] = invoice_match.group(0).upper()

    if "refund" in question.lower():
        result["refund_reason"] = state.get(
            "refund_reason",
            "Customer requested a refund and cancellation.",
        )

    return result


def supervisor_node(state: RouterState) -> dict:
    """Choose the next action using the request and workflow state."""

    # Step 1: A worker has returned; decide what happens next.
    if state.get("last_agent") == "billing":
        result = state.get("billing_result", {})

        if result.get("error"):
            return {
                "next_agent": "ask_user",
                "needs_clarification": True,
                "clarification_question": result["error"],
            }

        if state.get("department") == "refund":
            if not state.get("invoice_id"):
                return {
                    "next_agent": "ask_user",
                    "needs_clarification": True,
                    "clarification_question": (
                        "I found billing records. Which invoice or payment "
                        "would you like refunded?"
                    ),
                }

            payment_amount = state.get("payment_amount")

            if not state.get("refund_amount"):
                if payment_amount is None:
                    return {
                        "next_agent": "ask_user",
                        "needs_clarification": True,
                        "clarification_question": (
                            "I couldn't verify a payment amount for that "
                            "invoice. Please confirm which payment you mean."
                        ),
                    }

                return {
                    "next_agent": "ask_user",
                    "needs_clarification": True,
                    "clarification_question": (
                        f"I found a payment of {payment_amount:.2f} for "
                        f"{state['invoice_id']}. Please confirm that this "
                        "is the payment you want refunded."
                    ),
                }

            return {"next_agent": "refund"}

        return {"next_agent": "finish"}

    # Step 2: The refund workflow has returned.
    if state.get("last_agent") == "refund":
        return {"next_agent": "finish"}

    # Step 3: First request — classify it.
    prompt = f"""
Classify the user's request into exactly one category:
billing, accounts, support, refund, general, or unknown.

- billing: invoices, payments, charges, billing discrepancies
- accounts: subscriptions and account questions
- support: technical issues and troubleshooting
- refund: refund requests
- general: greetings and general questions
- unknown: cannot reasonably be classified

Return only the category.

User request: {state.get("question", "")}
"""

    print("[DEBUG] Supervisor: calling LLM", flush=True)
    response = get_llm().invoke(prompt)
    print("[DEBUG] Supervisor: LLM returned", flush=True)
    department = str(response.content).strip().lower()

    if department not in {
        "billing", "accounts", "support", "refund", "general", "unknown"
    }:
        department = "unknown"

    # Important: refund requests must go to the lookup node first.
    next_agent = {
        "refund": "billing_lookup",
        "billing": "billing",
        "accounts": "accounts",
        "support": "support",
        "general": "general",
        "unknown": "unknown",
    }[department]

    return {
        "department": department,
        "next_agent": next_agent,
    }


def billing_lookup_node(state: RouterState) -> dict:
    """Retrieve structured billing data for supervisor handoff."""
    customer_id = state.get("customer_id")
    invoice_id = state.get("invoice_id")

    # If only an invoice ID is supplied, retrieve the invoice.
    if invoice_id:
        invoice = get_invoice.invoke({"invoice_id": invoice_id})

        if not isinstance(invoice, dict) or invoice.get("error"):
            return {
                "last_agent": "billing",
                "billing_result": {
                    "error": f"Could not find invoice {invoice_id}."
                },
            }

        customer_id = customer_id or invoice.get("customer_id")

        if customer_id and invoice.get("customer_id") != customer_id:
            return {
                "last_agent": "billing",
                "billing_result": {
                    "error": (
                        "The supplied customer ID does not match "
                        "the customer associated with this invoice."
                    )
                },
            }

        payment = (
            get_payment.invoke({
                "customer_id": customer_id,
                "invoice_id": invoice_id,
            })
            if customer_id
            else {"error": "Customer ID could not be resolved."}
        )

    elif customer_id:
        transactions = get_transactions_by_customer_id.invoke(
            {"customer_id": customer_id}
        )

        if not isinstance(transactions, dict) or transactions.get("error"):
            return {
                "last_agent": "billing",
                "billing_result": {
                    "error": (
                        f"No transaction records were found for "
                        f"{customer_id}."
                    )
                },
            }

        # A customer may have multiple invoices. Do not arbitrarily
        # choose one when the user has not identified a payment.
        return {
            "last_agent": "billing",
            "billing_result": {
                "customer_id": customer_id,
                "transactions": transactions,
            },
            "needs_clarification": True,
            "clarification_question": (
                "I retrieved the customer's transaction records. "
                "Which invoice or payment should I use for the refund?"
            ),
        }

    else:
        return {
            "last_agent": "billing",
            "billing_result": {
                "error": (
                    "Please provide a customer ID or invoice ID so I can "
                    "look up the billing records."
                )
            },
        }

    if not isinstance(payment, dict) or payment.get("error"):
        payment = {}

    payment_amount = payment.get("amount")
    invoice_amount = invoice.get("amount")

    return {
        "last_agent": "billing",
        "customer_id": customer_id,
        "invoice_id": invoice_id,
        "invoice_amount": invoice_amount,
        "payment_amount": payment_amount,
        "invoice_status": invoice.get("status"),
        "payment_status": payment.get("status"),
        "billing_result": {
            "invoice": invoice,
            "payment": payment,
        },
    }


def general_node(state: RouterState) -> dict:
    response = get_llm().invoke(state["question"])
    return {
        "answer": (
            response.content
            if isinstance(response.content, str)
            else str(response.content)
        )
    }


def unknown_node(state: RouterState) -> dict:
    return {
        "answer": (
            "I can help with billing, accounts, support, and refund "
            "requests. Could you rephrase your question?"
        )
    }


def ask_user_node(state: RouterState) -> dict:
    return {
        "answer": state.get(
            "clarification_question",
            "Could you provide more details about your request?",
        ),
        "needs_clarification": True,
    }


def route_from_supervisor(
    state: RouterState,
) -> Literal[
    "billing_lookup", "billing", "accounts", "support",
    "general", "unknown", "refund", "ask_user", "finish"
]:
    action = state.get("next_agent", "unknown")

    if action in {
        "billing_lookup", "billing", "accounts", "support",
        "general", "unknown", "refund", "ask_user", "finish"
    }:
        return action

    return "unknown"


def after_billing(state: RouterState) -> str:
    if state.get("needs_clarification"):
        return "ask_user"
    return "supervisor"


def after_worker(state: RouterState) -> str:
    return "finish"


def build_router_graph():
    print("[DEBUG] Building router graph: START", flush=True)
    graph = StateGraph(RouterState)

    graph.add_node("supervisor", supervisor_node)
    graph.add_node("extract_identifiers", extract_identifiers)
    graph.add_node("billing_lookup", billing_lookup_node)
    graph.add_node("billing", billing_agent_node)
    graph.add_node("accounts", accounts_agent_node)
    graph.add_node("support", support_agent_node)
    graph.add_node("general", general_node)
    graph.add_node("unknown", unknown_node)
    graph.add_node("ask_user", ask_user_node)
    graph.add_node("refund", build_refund_approval_graph())
    print("[DEBUG] Registering nodes...", flush=True)

    graph.add_edge(START, "extract_identifiers")
    graph.add_edge("extract_identifiers", "supervisor")

    graph.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "billing_lookup": "billing_lookup",
            "billing": "billing",
            "accounts": "accounts",
            "support": "support",
            "general": "general",
            "unknown": "unknown",
            "refund": "refund",
            "ask_user": "ask_user",
            "finish": END,
        },
    )

    graph.add_conditional_edges(
        "billing_lookup",
        after_billing,
        {
            "supervisor": "supervisor",
            "ask_user": "ask_user",
        },
    )
    print("[DEBUG] Compiling graph...", flush=True)
    # Existing specialist nodes finish their own requests.
    for node in ("billing", "accounts", "support", "general", "unknown"):
        graph.add_edge(node, END)

    graph.add_edge("ask_user", END)
    graph.add_edge("refund", END)

    checkpointer = InMemorySaver()
    print("[DEBUG] Graph compilation complete", flush=True)
    return graph.compile(checkpointer=checkpointer)
