from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from app.config.settings import settings


# def get_llm():
#     llm = ChatOllama(
#         model="llama3.2:3b",
#         temperature=0,
#         base_url="http://localhost:11434"
#     )
#     return llm

def get_llm():
    if settings.model_provider == "ollama":
        return ChatOllama(
            model=settings.model_name,
            temperature=settings.temperature,
            )
    elif settings.model_provider == "openrouter":
        return ChatOpenAI(
            model=settings.model_name,
            temperature=settings.temperature,
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
        )
    raise ValueError(f"Unsupported model provider: {settings.model_provider}")
