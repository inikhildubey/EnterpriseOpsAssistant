# app/graph/refund_approval.py

from typing import Literal

from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt
from typing_extensions import TypedDict


class RefundState(TypedDict, total=False):
    customer_id: str
    invoice_id: str
    refund_amount: float
    refund_reason: str
    approval_status: Literal["approved", "rejected"]
    RouterState: str
    answer: str


def prepare_refund(state: RefundState) -> dict:
    """Prepare the refund proposal; do not execute anything."""

    return {"RouterState": "pending_approval", "answer": (f"Refund proposal: {state['refund_amount']:.2f} "
                                                     f"for invoice {state['invoice_id']} "
                                                     f"(customer: {state['customer_id']}). "
                                                     f"Reason: {state['refund_reason']}"), }


def request_approval(state: RefundState) -> dict:
    """Pause execution until a human approves or rejects."""

    decision = interrupt(
        {"type": "refund_approval", "customer_id": state["customer_id"], "invoice_id": state["invoice_id"],
         "amount": state["refund_amount"], "reason": state["refund_reason"], })

    if not isinstance(decision, dict) or decision.get("approved") not in (True, False,):
        raise ValueError("Approval decision must contain a boolean 'approved'.")

    return {"approval_status": "approved" if decision["approved"] else "rejected"}


def route_after_approval(state: RefundState, ) -> Literal["execute_refund", "reject_refund"]:
    if state.get("approval_status") == "approved":
        return "execute_refund"
    return "reject_refund"


def execute_refund(state: RefundState) -> dict:
    """Simulate a refund. No real payment system is called."""

    return {"RouterState": "refund_simulated", "answer": (f"SIMULATED refund of {state['refund_amount']:.2f} "
                                                     f"for invoice {state['invoice_id']} completed."), }


def reject_refund(state: RefundState) -> dict:
    return {"RouterState": "rejected", "answer": (f"Refund request for invoice {state['invoice_id']} "
                                             "was rejected. No refund was executed."), }


def build_refund_approval_graph():
    workflow = StateGraph(RefundState)

    workflow.add_node("prepare_refund", prepare_refund)
    workflow.add_node("request_approval", request_approval)
    workflow.add_node("execute_refund", execute_refund)
    workflow.add_node("reject_refund", reject_refund)

    workflow.add_edge(START, "prepare_refund")
    workflow.add_edge("prepare_refund", "request_approval")

    workflow.add_conditional_edges("request_approval", route_after_approval,
                                   {"execute_refund": "execute_refund", "reject_refund": "reject_refund", }, )

    workflow.add_edge("execute_refund", END)
    workflow.add_edge("reject_refund", END)

    # checkpointer = InMemorySaver()
    # return workflow.compile(checkpointer=checkpointer)
    return workflow.compile()
