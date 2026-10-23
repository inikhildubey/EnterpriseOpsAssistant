# app/graph/state.py
from typing import TypedDict


class BillingState(TypedDict, total=False):
    question: str
    invoice_id: str
    customer_id: str
    invoice_amount: float
    payment_amount: float
    discrepancy: float
    answer: str

    # Human approval workflow
    refund_amount: float
    refund_reason: str
    approval_status: str


class AccountsState(TypedDict, total=False):
    question: str
    customer_id: str
    subscription_status: str
    answer: str


class SupportState(TypedDict, total=False):
    question: str
    issue_description: str
    answer: str



class RouterState(TypedDict, total=False):
    # Original request and supervisor routing
    question: str
    department: str
    next_agent: str
    answer: str

    # Customer and invoice identifiers
    customer_id: str
    invoice_id: str

    # Billing agent results
    invoice_amount: float
    payment_amount: float
    discrepancy: float
    invoice_status: str
    payment_status: str
    billing_result: dict

    # Refund workflow
    refund_amount: float
    refund_reason: str
    approval_status: str
    status: str

    # Supervisor workflow tracking
    last_agent: str
    needs_clarification: bool
    clarification_question: str
    workflow_complete: bool


