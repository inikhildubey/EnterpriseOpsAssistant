from langchain_core.tools import tool

from app.rag.retriver import format_documents, get_billing_retriever


@tool
def search_billing_knowledge(question: str) -> str:
    """Search the billing knowledge base for billing policies,
    invoice explanations, payment rules, and documented procedures.
    Use this when answering requires company-specific billing knowledge."""

    retriever = get_billing_retriever()
    documents = retriever.invoke(question)

    if not documents:
        return "No relevant billing knowledge was found."

    return format_documents(documents)
