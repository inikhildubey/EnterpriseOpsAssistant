from app.agents.accounts import get_accounts_agent
from app.graph.state import RouterState


def accounts_agent_node(state: RouterState) -> dict:
    result = get_accounts_agent().invoke({
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
        "I couldn't generate an accounts response right now. Please try again.",
    )

    return {"answer": answer}