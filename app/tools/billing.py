from langchain_core.tools import tool


INVOICES = {
    "INV-12344": {
            "invoice_id": "INV-12344",
            "customer_id": "CUST-1002",
            "amount": 249.00,
            "currency": "USD",
            "status": "paid",
            "billing_period": "2026-09-01 to 2026-09-30",
        },
    "INV-12345": {
        "invoice_id": "INV-12345",
        "customer_id": "CUST-1001",
        "amount": 319.00,
        "currency": "USD",
        "status": "paid",
        "billing_period": "2026-09-01 to 2026-09-30",
    },
    "INV-12346": {
        "invoice_id": "INV-12346",
        "customer_id": "CUST-1001",
        "amount": 319.00,
        "currency": "USD",
        "status": "overdue",
        "billing_period": "2026-10-01 to 2026-10-31",
    },
    "INV-12347": {
        "invoice_id": "INV-12347",
        "customer_id": "CUST-1002",
        "amount": 249.00,
        "currency": "USD",
        "status": "paid",
        "billing_period": "2026-10-01 to 2026-10-31",
    },
}

SUBSCRIPTIONS = {
    "CUST-1001" : {
    "customer_id": "CUST-1001",
    "invoice_id": "INV-12346",
    "status": "active",
    "plan": "Premium",
    "billing_cycle": "monthly",
},
"CUST-1002" : {
    "customer_id": "CUST-1002",
    "invoice_id": "INV-12347",
    "status": "active",
    "plan": "Basic",
    "billing_cycle": "monthly",
}
}

TRANSACTIONS = {
    "CUST-1001":{"INV-12345": {
        "invoice_id": "INV-12345",
        "customer_id": "CUST-1001",
        "transaction_id": "TXN-54321",
        "amount": 249.00,
        "currency": "USD",
        "status": "completed",
        "date": "2026-09-15",
    }},
    "CUST-1002":{"INV-12344":{
        "invoice_id": "INV-12344",
        "customer_id": "CUST-1002",
        "transaction_id": "TXN-54320",
        "amount": 249.00,
        "currency": "USD",
        "status": "completed",
        "date": "2026-09-08",
    },
    "INV-12347":{
        "invoice_id": "INV-12347",
        "customer_id": "CUST-1002",
        "transaction_id": "TXN-54399",
        "amount": 249.00,
        "currency": "USD",
        "status": "completed",
        "date": "2026-09-03",
    }}
}


@tool
def get_invoice(invoice_id: str) -> dict:
    """
    Get an invoice by invoice ID.

    Returns the invoice amount, payment status, billing period,
    and customer_id.

    Use this when you need invoice information or need to find
    the customer_id associated with an invoice.
    """

    invoice = INVOICES.get(invoice_id)

    if not invoice:
        return {
            "error": f"Invoice {invoice_id} was not found."
        }

    return invoice


@tool
def get_subscription(customer_id: str) -> dict:
    """Retrieve the customer's current subscription details."""
    subscription = SUBSCRIPTIONS.get(customer_id)
    if not subscription:
        return {
            "error": f"Subscription for customer {customer_id} was not found."
        }   
    return subscription

@tool
def get_payment_status(invoice_id: str) -> dict:
    """
    Retrieve the current payment status recorded on an invoice.

    Use this tool only when you need to know whether an invoice
    is marked as paid, overdue, pending, or another payment status.

    This tool does NOT provide transaction amount or payment
    transaction history.
    """

    invoice = INVOICES.get(invoice_id)
    if not invoice:
        return {
            "error": f"Invoice {invoice_id} was not found."
        }
    return {
        "invoice_id": invoice_id,
        "status": invoice["status"],
        "amount": invoice["amount"],
        "currency": invoice["currency"],
    }

@tool
def get_payment(customer_id: str, invoice_id: str) -> dict:
    """
    Get the actual payment transaction for a customer and invoice.

    Returns the amount actually recorded as paid, transaction ID,
    payment status, and transaction date.

    Use this to compare the invoice amount with the amount actually paid.
    """

    customer_transactions = TRANSACTIONS.get(customer_id)

    if not customer_transactions:
        return {
            "error": f"No transactions found for customer {customer_id}."
        }

    transaction = customer_transactions.get(invoice_id)

    if not transaction:
        return {
            "error": (
                f"Transaction for customer {customer_id} "
                f"and invoice {invoice_id} was not found."
            )
        }

    return transaction
