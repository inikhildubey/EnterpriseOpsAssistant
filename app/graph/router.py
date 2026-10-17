from langgraph.graph import StateGraph, START, END

from app.graph.state import RouterState
from app.graph.billing import billing_agent_node
from app.graph.accounts import accounts_agent_node
from app.graph.support import support_agent_node
from app.models.factory import get_llm


def router_node(state: RouterState) -> dict:
    prompt = f"""
    Classify the user's request into exactly one category:
    billing, accounts, support, or unknown.

    User request: {state["question"]}

    Return only the category.
    """

    response = get_llm().invoke(prompt)
    department = response.content.strip().lower()

    if department not in {"billing", "accounts", "support"}:
        department = "unknown"

    return {"department": department}


def unknown_node(state: RouterState) -> dict:
    return {
        "answer": (
            "I can currently help with billing, accounts, "
            "and support questions. Could you rephrase your request?"
        )
    }


def build_router_graph():
    graph = StateGraph(RouterState)

    graph.add_node("router", router_node)
    graph.add_node("billing", billing_agent_node)
    graph.add_node("accounts", accounts_agent_node)
    graph.add_node("support", support_agent_node)
    graph.add_node("unknown", unknown_node)

    graph.add_edge(START, "router")

    graph.add_conditional_edges(
        "router",
        lambda state: state["department"],
        {
            "billing": "billing",
            "accounts": "accounts",
            "support": "support",
            "unknown": "unknown",
        },
    )
    for node in ("billing", "accounts", "support", "unknown"):
        graph.add_edge(node, END)

    return graph.compile()