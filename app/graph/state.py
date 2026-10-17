from typing import TypedDict


class BillingState(TypedDict, total=False):

    question: str

    invoice_id: str
    customer_id: str

    invoice_amount: float
    payment_amount: float

    payment_status: str
    transaction_id: str

    discrepancy: float
    department: str
    answer: str
