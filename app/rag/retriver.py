from langchain_core.retrievers import BaseRetriever

from app.rag.vector_store import get_vector_store


def get_billing_retriever() -> BaseRetriever:
    vector_store = get_vector_store()

    return vector_store.as_retriever(
        search_kwargs={
            "k": 3,
        }
    )