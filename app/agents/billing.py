from langchain.agents import create_agent

from app.models.factory import get_llm
from app.tools.billing import (
    get_invoice,
    get_payment_status,
    get_subscription,
    get_payment,
)

def get_billing_agent():
    llm = get_llm()
    print(llm)
    tools = [
        get_invoice,
        # get_payment_status,
        # get_subscription,
        get_payment,
    ]

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt="""
                You are a billing support agent.

                Your job is to investigate customer billing questions using
                the available billing tools.

                Investigation rules:

                - Use tools whenever the answer depends on customer-specific data.
                - Never assume that an invoice being marked "paid" means the
                full invoice amount was actually paid.
                - When investigating a payment discrepancy:
                    1. Retrieve the invoice using get_invoice.
                    2. Read the customer_id from the invoice result.
                    3. Retrieve the payment using get_payment with that customer_id
                    and the same invoice_id.
                    4. Compare the invoice amount with the actual payment amount.
                    5. Only then explain the discrepancy.
                - Do not invent payment or transaction information.
                - Do not claim that a payment was partial, outstanding, refunded,
                or incorrectly applied unless the available tool data supports it.
                - If required information cannot be obtained from the available
                tools, clearly state what information is missing.
                """,
    )

    return agent
