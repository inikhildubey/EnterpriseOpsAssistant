
from langgraph.graph import StateGraph, START, END

from app.graph.state import BillingState
from app.models.factory import get_llm
from app.tools.billing import get_invoice, get_payment


# -----------------------------
# Billing workflow nodes
# -----------------------------

def get_invoice_node(state: BillingState) -> BillingState:
    print("Getting invoice")

    result = get_invoice.invoke({
        "invoice_id": state["invoice_id"]
    })

    if "error" in result:
        return {"answer": result["error"]}

    return {
        "customer_id": result["customer_id"],
        "invoice_amount": result["amount"],
        "payment_status": result["status"],
    }


def route_after_invoice(state: BillingState) -> str:
    if state.get("answer"):
        return "stop"

    return "continue"


def get_payment_node(state: BillingState) -> BillingState:
    print("Getting payment")

    result = get_payment.invoke({
        "customer_id": state["customer_id"],
        "invoice_id": state["invoice_id"],
    })

    if "error" in result:
        return {"answer": result["error"]}

    return {
        "payment_amount": result["amount"],
        "transaction_id": result["transaction_id"],
    }


def route_after_payment(state: BillingState) -> str:
    if state.get("answer"):
        return "stop"

    return "continue"


def compare_payment_node(state: BillingState) -> BillingState:
    print("Comparing invoice and payment")

    discrepancy = (
        state["invoice_amount"] - state["payment_amount"]
    )

    return {"discrepancy": discrepancy}


# -----------------------------
# LLM Router
# -----------------------------

def router_node(state: BillingState) -> BillingState:
    llm = get_llm()

    prompt = f"""
Classify the user's request into exactly one department.

- billing: invoices, payments, charges, refunds, billing disputes
- accounts: customer accounts, subscriptions, account status
- support: technical issues, service problems, incidents
- unknown: anything else

User question:
{state["question"]}

Return only one word:
billing, accounts, support, or unknown.
"""

    response = llm.invoke(prompt)
    department = response.content.strip().lower()

    if department not in {
        "billing", "accounts", "support", "unknown"
    }:
        department = "unknown"

    return {"department": department}


def route_request(state: BillingState) -> str:
    return state["department"]


# -----------------------------
# Final Response
# -----------------------------

def final_response_node(state: BillingState) -> BillingState:
    llm = get_llm()

    prompt = f"""
You are a helpful billing support assistant.

Explain the verified information below clearly and concisely.
Do not invent facts or claim that money is owed, refunded,
or duplicated unless the evidence explicitly establishes it.

User question:
{state["question"]}

Verified information:
Invoice ID: {state["invoice_id"]}
Invoice amount: ${state["invoice_amount"]}
Invoice payment status: {state["payment_status"]}
Recorded payment amount: ${state["payment_amount"]}
Transaction ID: {state["transaction_id"]}
Difference (invoice minus payment): ${state["discrepancy"]}

Explain the difference without assuming its cause.
"""

    response = llm.invoke(prompt)

    return {"answer": response.content}


# -----------------------------
# Build Graph
# -----------------------------

def build_billing_graph():
    graph = StateGraph(BillingState)

    graph.add_node("router", router_node)
    graph.add_node("get_invoice", get_invoice_node)
    graph.add_node("get_payment", get_payment_node)
    graph.add_node("compare_payment", compare_payment_node)
    graph.add_node("final_response", final_response_node)

    graph.add_edge(START, "router")

    graph.add_conditional_edges(
        "router",
        route_request,
        {
            "billing": "get_invoice",
            "accounts": END,
            "support": END,
            "unknown": END,
        },
    )

    graph.add_conditional_edges(
        "get_invoice",
        route_after_invoice,
        {
            "continue": "get_payment",
            "stop": END,
        },
    )

    graph.add_conditional_edges(
        "get_payment",
        route_after_payment,
        {
            "continue": "compare_payment",
            "stop": END,
        },
    )

    graph.add_edge("compare_payment", "final_response")
    graph.add_edge("final_response", END)

    return graph.compile()


