from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter


KB_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "billing"
    / "billing_knowledge_base.md"
)


def load_billing_documents() -> list[Document]:
    text = KB_PATH.read_text(encoding="utf-8")

    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[
            ("#", "title"),
            ("##", "section"),
            ("###", "subsection"),
        ],
        strip_headers=False,
    )

    documents = splitter.split_text(text)

    for document in documents:
        document.metadata.update(
            {
                "source": "billing_knowledge_base.md",
                "department": "billing",
                "document_type": "policy",
                "version": "1.0",
            }
        )

    return documents