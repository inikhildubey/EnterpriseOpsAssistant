from langchain_core.runnables import RunnablePassthrough

from app.models.factory import get_llm
from app.prompts.billing import prompt
from app.rag.retriver import get_billing_retriever
from app.schema.billing import BillingResponse


def get_billing_chain():
    retriever = get_billing_retriever()
    import pdb; pdb.set_trace()
    llm = get_llm()
    structured_llm = llm.with_structured_output(BillingResponse)

    chain = (
        {
            "context": retriever,
            "question": RunnablePassthrough(),
        }
        | prompt
        | structured_llm
    )

    return chain