from app.agents.support import get_support_agent
from app.graph.state import RouterState


def support_agent_node(state: RouterState) -> dict:
    result = get_support_agent().invoke({
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
        "I couldn't generate a support response. Please try again.",
    )

    return {"answer": answer}