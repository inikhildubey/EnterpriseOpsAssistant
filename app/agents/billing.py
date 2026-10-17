
from langchain.agents import create_agent
from app.tools.knowledge import search_billing_knowledge
from app.models.factory import get_llm
from app.tools.billing import (
    get_invoice,
    get_subscription,
    get_transaction_details,
    get_payment,
)


def get_billing_agent():
    llm = get_llm()

    tools = [
        get_invoice,
        get_subscription,
        get_transaction_details,
        get_payment,
        search_billing_knowledge,
    ]

    agent = create_agent(
        model=llm,
        tools=tools,
        # middleware=[InlineToolCallRepairMiddleware()]
        system_prompt="""
                            You are a billing support agent.
                            
                            Investigate customer billing questions using the available tools.
                            
                            Rules:
                            - Use tools whenever the answer depends on customer-specific data.
                            - For invoice questions, use get_invoice.
                            - For subscription questions, use get_subscription.
                            - get_transaction_details returns the invoice's recorded status
                              and invoice amount. It does not return the actual payment transaction.
                            - For actual payment amounts, transaction IDs, and transaction dates,
                              use get_payment.
                            - For a payment discrepancy:
                              1. Call get_invoice with the invoice ID.
                              2. Read customer_id from the invoice result.
                              3. Call get_payment with that customer_id and the same invoice_id.
                              4. Compare the invoice amount with the actual payment amount.
                              5. Explain only what the retrieved data supports.
                            - Never invent payment or transaction information.
                            - Do not claim a balance is due, a duplicate charge occurred,
                              or a refund is warranted unless the evidence supports that conclusion.
                            - If a tool returns an error, explain the missing information.
                            - Do not claim an investigation is complete until the required
                              tool calls have actually been executed.
                            - Use search_billing_knowledge for company-specific billing policies,
                              payment rules, invoice procedures, and documented billing guidance.
                            - If the retrieved knowledge does not support a clear answer,
                              explain the limitation instead of guessing.
                            - Combine retrieved billing knowledge with customer-specific tool results
                              when both are needed to answer the question.
                        """,
    )

    return agent
