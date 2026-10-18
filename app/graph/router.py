# app/graph/router.py

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

from app.graph.refund_approval import build_refund_approval_graph
from app.graph.state import RouterState
from app.graph.billing import billing_agent_node
from app.graph.accounts import accounts_agent_node
from app.graph.support import support_agent_node
from app.models.factory import get_llm


# def router_node(state: RouterState) -> dict:
#     prompt = f"""
#     Classify the user's request into exactly one category:
#     billing, accounts, support, refund, general, or unknown.
#
#     Use:
#     - billing for invoices, payments, charges, and billing questions
#     - accounts for subscriptions and account-related questions
#     - support for technical issues and troubleshooting
#     - refund for refund requests
#     - general for greetings, casual conversation, and general questions
#     - unknown only when the request cannot reasonably be classified
#
#     User request: {state["question"]}
#
#     Return only the category.
#     """
#
#     response = get_llm().invoke(prompt)
#     department = response.content.strip().lower()
#
#     if department not in {"billing", "accounts", "support", "refund", "general"}:
#         department = "unknown"
#
#     return {"department": department}

def supervisor_node(state: RouterState) -> dict:
    prompt = f"""
    You are the supervisor of an enterprise operations assistant.

    Classify the user's request into exactly one category:
    billing, accounts, support, refund, general, or unknown.

    Routing rules:
    - billing: invoices, payments, charges, billing discrepancies
    - accounts: subscriptions and account-related questions
    - support: technical issues and troubleshooting
    - refund: refund requests
    - general: greetings and general questions
    - unknown: requests that cannot reasonably be classified

    User request:
    {state["question"]}

    Return only the category.
    """

    response = get_llm().invoke(prompt)
    department = response.content.strip().lower()

    allowed_departments = {
        "billing",
        "accounts",
        "support",
        "refund",
        "general",
        "unknown",
    }

    if department not in allowed_departments:
        department = "unknown"

    return {"department": department}

def unknown_node(state: RouterState) -> dict:
    return {
        "answer": (
            "I can currently help with billing, accounts, "
            "and support questions. Could you rephrase your request?"
        )
    }


# def prepare_refund_node(state: RouterState) -> dict:
#     required = (
#         state.get("invoice_id"),
#         state.get("customer_id"),
#         state.get("refund_amount"),
#         state.get("refund_reason"),
#     )
#
#     if any(value is None or value == "" for value in required):
#         return {
#             "refund_ready": False,
#             "approval_status": "missing_details",
#             "answer": (
#                 "Please provide invoice ID, customer ID, "
#                 "refund amount, and refund reason."
#             ),
#         }
#
#     if state["refund_amount"] <= 0:
#         return {
#             "refund_ready": False,
#             "approval_status": "invalid_amount",
#             "answer": "The refund amount must be greater than zero.",
#         }
#
#     return {"refund_ready": True}
#
#
# def refund_approval_node(state: RouterState) -> dict:
#     decision = interrupt({
#         "type": "refund_approval_required",
#         "invoice_id": state["invoice_id"],
#         "customer_id": state["customer_id"],
#         "refund_amount": state["refund_amount"],
#         "refund_reason": state["refund_reason"],
#         "message": "Approve or reject this simulated refund?",
#     })
#
#     approved = (
#         decision is True
#         or (
#             isinstance(decision, dict)
#             and decision.get("approved") is True
#         )
#     )
#
#     return {
#         "approval_status": "approved" if approved else "rejected"
#     }
#
#
# def process_refund_node(state: RouterState) -> dict:
#     # Demo only: no real payment or refund is executed.
#     if state["approval_status"] == "approved":
#         return {
#             "answer": (
#                 f"Simulated refund approved for "
#                 f"{state['refund_amount']:.2f}. "
#                 f"Invoice: {state['invoice_id']}. "
#                 "No real payment was refunded."
#             )
#         }
#
#     return {
#         "answer": (
#             f"Refund request for invoice {state['invoice_id']} "
#             "was rejected. No refund was executed."
#         )
#     }

# def refund_node(state: RouterState) -> dict:
#     refund_graph = build_refund_approval_graph()
#
#     result = refund_graph.invoke({
#         "customer_id": state["customer_id"],
#         "invoice_id": state["invoice_id"],
#         "amount": state["refund_amount"],
#         "reason": state["refund_reason"],
#     })
#
#     return {
#         "approval_status": result.get("approval", ""),
#         "answer": result.get("message", ""),
#     }

def general_node(state: RouterState) -> dict:
    response = get_llm().invoke(state["question"])

    return {
        "answer": (
            response.content
            if isinstance(response.content, str)
            else str(response.content)
        )
    }


def refund_details_node(state: RouterState) -> dict:
    return {
        "answer": (
            "I can help start a refund request. "
            "Please provide the customer ID, invoice ID, "
            "refund amount, and reason for the refund."
        )
    }


def build_router_graph():
    graph = StateGraph(RouterState)

    graph.add_node("router", supervisor_node)
    graph.add_node("billing", billing_agent_node)
    graph.add_node("accounts", accounts_agent_node)
    graph.add_node("support", support_agent_node)
    graph.add_node("general", general_node)
    graph.add_node("unknown", unknown_node)
    graph.add_node("refund_details", refund_details_node)
    graph.add_node("refund", build_refund_approval_graph())

    graph.add_edge(START, "router")

    def route_request(state: RouterState) -> str:
        department = state["department"]

        if department == "refund":
            required = (
                state.get("customer_id"),
                state.get("invoice_id"),
                state.get("refund_amount"),
                state.get("refund_reason"),
            )

            if any(value is None or value == "" for value in required):
                return "refund_details"

        if department in {
            "billing",
            "accounts",
            "support",
            "general",
            "unknown",
            "refund",
        }:
            return department

        return "unknown"

    graph.add_conditional_edges(
        "router",
        route_request,
        {
            "billing": "billing",
            "accounts": "accounts",
            "support": "support",
            "general": "general",
            "unknown": "unknown",
            "refund_details": "refund_details",
            "refund": "refund",
        },
    )

    for node in (
            "billing",
            "accounts",
            "support",
            "general",
            "unknown",
            "refund_details",
            "refund",
    ):
        graph.add_edge(node, END)

    checkpointer = InMemorySaver()
    return graph.compile(checkpointer=checkpointer)
