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
    question: str
    department: str
    answer: str

    customer_id: str
    invoice_id: str
    refund_amount: float
    refund_reason: str
    approval_status: str
    status: str

