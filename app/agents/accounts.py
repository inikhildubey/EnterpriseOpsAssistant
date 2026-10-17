
from langchain.agents import create_agent

from app.models.factory import get_llm
from app.tools.billing import get_subscription


def get_accounts_agent():
    return create_agent(
        model=get_llm(),
        tools=[get_subscription],
        system_prompt="""You are an accounts support agent.
Handle customer account and subscription questions.
Use tools to verify subscription details.
Never invent account data or claim an action was completed
unless a tool confirms it.
If the available tools cannot answer the question,
explain the limitation clearly."""
    )
