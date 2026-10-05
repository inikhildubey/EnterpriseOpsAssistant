from langchain_core.messages import ToolMessage

from app.agents.billing import get_billing_agent
from app.models.factory import get_llm
from app.tools.billing import get_invoice, get_payment
from app.tools.billing import (get_payment_status, get_subscription)

llm = get_llm()


# def main():
# Test LLM
# question = "why my bill amount is high"
# structured_llm = llm.with_structured_output(BillingResponse)

# chain = prompt | structured_llm
# response = chain.invoke({"question": question})
# print(response)

# data Ingestion
# ingest_billing_documents()

# check semantic similarity from Vector DB
# vector_store = get_vector_store()
# response = vector_store.similarity_search("why my bill amount is high")
# print(response)

# retriever = get_billing_retriever()

# documents = retriever.invoke(
#     "Why is my bill higher this month?"
# )
# print(documents)
#
# chain = get_billing_chain()

# response = chain.invoke(
#     "Why is my bill higher this month?"
# )

# print(response)
# print("Function Call ->", get_invoice, end="\n")
# print("Function Name ->",get_invoice.name, end="\n")
# print("Function Description ->",get_invoice.description, end="\n")
# print("Function Args ->",get_invoice.args, end="\n")
# result = get_invoice.invoke({
#     "invoice_id": "INV-12345"
# })
# print(result)
# pass


def test_manual_agent_single_tools():
    user_query = "Use get_invoice to retrieve invoice INV-12345. " \
                 "Then use get_transaction_details with customer_id CUST-1001 and invoice_id INV-12345. " \
                 "Compare the invoice amount with the transaction amount and explain the discrepancy."
    llm_with_tools = llm.bind_tools([get_invoice, ])
    response = llm_with_tools.invoke(user_query)
    tool_call = response.tool_calls[0]
    result = get_invoice.invoke(tool_call["args"])
    tool_message = ToolMessage(content=str(result), tool_call_id=tool_call["id"], )

    final_response = llm_with_tools.invoke([("user", user_query), response, tool_message, ])
    print(final_response)


def test_manual_agent_multiple_tools():
    user_query = ("Use get_invoice to retrieve invoice INV-12345. "
                  "Then use get_transaction_details with customer_id CUST-1001 "
                  "and invoice_id INV-12345. "
                  "Compare the invoice amount with the transaction amount "
                  "and explain the discrepancy.")

    tools = [get_invoice, get_payment_status, get_subscription, get_transaction_details, ]

    tools_by_name = {tool.name: tool for tool in tools}

    llm_with_tools = llm.bind_tools(tools)

    messages = [("user", user_query)]

    while True:
        response = llm_with_tools.invoke(messages)

        messages.append(response)

        if not response.tool_calls:
            break

        for tool_call in response.tool_calls:
            tool = tools_by_name[tool_call["name"]]

            result = tool.invoke(tool_call["args"])

            tool_message = ToolMessage(content=str(result), tool_call_id=tool_call["id"], )

            messages.append(tool_message)

    print(messages)
    print(messages[-1])


def test_agent_abstract_orchestration():
    agent = get_billing_agent()

    result = agent.invoke({"messages": [{"role": "user",
                                         #   "content": (# "Use get_invoice to retrieve invoice INV-12345. "
                                         # "Then use get_transaction_details with customer_id CUST-1001"
                                         # "and invoice_id INV-12345."
                                         # "Compare the invoice amount with the transaction amount"
                                         # "and explain the discrepancy."
                                         # "My invoice INV-12345 says I was charged $319, but I only paid $249. Can you check what's going on?"), }]})
                                         "content": (
                                             "Use get_invoice to retrieve invoice INV-12345. "
                                             "Then use the customer_id returned by that tool "
                                             "to call get_payment for the same invoice. "
                                             "Compare the invoice amount with the payment amount "
                                             "and explain the discrepancy."), }]})
    print(result)


def test_second_tool_call_manually():
    llm = get_llm()

    llm_with_tools = llm.bind_tools(
        [
            get_invoice,
            get_payment,
        ]
    )
    # response = llm_with_tools.invoke(
    #     "Call get_payment for customer_id CUST-1001 "
    #     "and invoice_id INV-12345."
    # )

    # print(response)
    # print(response.tool_calls)
    response1 = llm_with_tools.invoke("Use get_invoice to retrieve invoice INV-12345.")

    print("FIRST RESPONSE:")
    print(response1)
    print("\nTOOL CALLS:")
    print(response1.tool_calls)

    tool_call = response1.tool_calls[0]

    result = get_invoice.invoke(tool_call["args"])

    tool_message = ToolMessage(
        content=str(result),
        tool_call_id=tool_call["id"],
    )

    messages = [
        (
            "user",
            "My invoice INV-12345 says I was charged $319, "
            "but I only paid $249. Check what is going on."
        ),
        response1,
        tool_message,
    ]

    response2 = llm_with_tools.invoke(messages)

    print("\nSECOND RESPONSE:")
    print(response2)

    print("\nSECOND TOOL CALLS:")
    print(response2.tool_calls)


def tset_third_tool_call_manually():
    llm = get_llm()

    llm_with_tools = llm.bind_tools(
        [
            get_invoice,
            get_payment,
        ]
    )

    # ---------------------------------------------------------
    # 1. First turn: ask the model to retrieve the invoice
    # ---------------------------------------------------------
    response1 = llm_with_tools.invoke("Use get_invoice to retrieve invoice INV-12345.")

    print("FIRST RESPONSE:")
    print(response1)

    print("\nFIRST TOOL CALLS:")
    print(response1.tool_calls)

    # ---------------------------------------------------------
    # 2. Execute the first tool call
    # ---------------------------------------------------------
    tool_call = response1.tool_calls[0]

    result = get_invoice.invoke(tool_call["args"])

    print("\nFIRST TOOL RESULT:")
    print(result)

    tool_message = ToolMessage(
        content=str(result),
        tool_call_id=tool_call["id"],
    )

    # ---------------------------------------------------------
    # 3. Give the tool result back to the model
    #    and explicitly ask for the SECOND tool call
    # ---------------------------------------------------------
    messages = [
        ("user", "I need to investigate invoice INV-12345."),
        response1,
        tool_message,
        (
            "user",
            "Now call get_payment using the customer_id "
            "from the invoice result and the same invoice_id.",
        ),
    ]

    response2 = llm_with_tools.invoke(messages)

    print("\nSECOND RESPONSE:")
    print(response2)

    print("\nSECOND TOOL CALLS:")
    print(response2.tool_calls)


if __name__ == "__main__":
    # test_manual_agent_single_tools()
    # test_manual_agent_multiple_tools()
    test_agent_abstract_orchestration()
    # test_second_tool_call_manually()
    # tset_third_tool_call_manually()
