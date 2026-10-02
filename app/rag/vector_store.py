from pathlib import Path

from langchain_chroma import Chroma

from app.embeddings.factory import get_embeddings


VECTOR_STORE_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "vector_store"
)


def get_vector_store() -> Chroma:
    return Chroma(
        collection_name="billing_knowledge",
        embedding_function=get_embeddings(),
        persist_directory=str(VECTOR_STORE_PATH),
    )