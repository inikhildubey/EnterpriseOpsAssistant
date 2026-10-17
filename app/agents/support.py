
from langchain.agents import create_agent

from app.models.factory import get_llm


def get_support_agent():
    return create_agent(
        model=get_llm(),
        tools=[],
        system_prompt="""You are a technical support agent.
Help users understand technical issues using the
information they provide.
Do not claim to inspect logs, systems, or service
status because no such tools are available.
If diagnosis requires unavailable information,
ask a concise clarifying question."""
    )
