from app.rag.loder import load_billing_documents
from app.rag.vector_store import get_vector_store


def ingest_billing_documents() -> None:
    documents = load_billing_documents()

    vector_store = get_vector_store()

    vector_store.add_documents(documents)

    print(f"Ingested {len(documents)} documents.")