from langchain_core.retrievers import BaseRetriever

from app.rag.vector_store import get_vector_store


def get_billing_retriever() -> BaseRetriever:
    vector_store = get_vector_store()

    return vector_store.as_retriever(
        search_kwargs={
            "k": 3,
        }
    )


def format_documents(documents):
    formatted_documents = []

    for document in documents:
        formatted_documents.append(
            f"""
        Source: {document.metadata.get("source")}
        Section: {document.metadata.get("section")}
        Subsection: {document.metadata.get("subsection")}

        {document.page_content}
        """.strip()
                )

    return "\n\n---\n\n".join(formatted_documents)