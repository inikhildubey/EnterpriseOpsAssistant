from langgraph.graph import StateGraph, START, END

from app.graph.state import BillingState
from app.models.factory import get_llm
from app.agents.billing import get_billing_agent


# def router_node(state: BillingState) -> BillingState:
#     print("Routing request...")
#
#     llm = get_llm()
#
#     prompt = f"""Classify this request into exactly one department:
# billing, accounts, support, or unknown.
#
# User question: {state["question"]}
#
# Return only one word."""
#
#     response = llm.invoke(prompt)
#     department = response.content.strip().lower()
#
#     if department not in {"billing", "accounts", "support", "unknown"}:
#         department = "unknown"
#
#     print(f"Department: {department}")
#     return {"department": department}


# def unsupported_department_node(state: BillingState) -> BillingState:
#     department = state.get("department", "unknown")
#
#     return {
#         "answer": (
#             f"The {department} workflow is not implemented yet. "
#             "Currently, I can handle billing questions."
#         )
#     }


# def route_request(state: BillingState) -> str:
#     return state["department"]


# def build_billing_graph():
#     graph = StateGraph(BillingState)
#
#     graph.add_node("router", router_node)
#     graph.add_node("billing_agent", billing_agent_node)
#     graph.add_node("unsupported", unsupported_department_node)
#
#     graph.add_edge(START, "router")
#
#     graph.add_conditional_edges(
#         "router",
#         route_request,
#         {
#             "billing": "billing_agent",
#             "accounts": "unsupported",
#             "support": "unsupported",
#             "unknown": "unsupported",
#         },
#     )
#
#     graph.add_edge("billing_agent", END)
#     graph.add_edge("unsupported", END)
#
#     return graph.compile()

def billing_agent_node(state: BillingState) -> BillingState:
    print("Running billing agent...")

    agent = get_billing_agent()

    result = agent.invoke({
        "messages": [
            {"role": "user", "content": state["question"]}
        ]
    })

    messages = result.get("messages", [])
    answer = next(
        (
            message.content
            for message in reversed(messages)
            if getattr(message, "type", None) == "ai"
            and isinstance(message.content, str)
            and message.content.strip()
        ),
        "I couldn't generate a billing response. Please try again.",
    )
    print("Billing agent completed.")
    return {"answer": answer}
