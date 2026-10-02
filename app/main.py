from app.models.factory import get_llm
from app.prompts.billing import prompt
from app.rag.chain import get_billing_chain
from app.rag.ingest import ingest_billing_documents
from app.rag.loder import load_billing_documents
from app.rag.retriver import get_billing_retriever
from app.rag.vector_store import get_vector_store
from app.schema.billing import BillingResponse



llm = get_llm()
def main():
   #Test LLM
    # question = "why my bill amount is high"
    # structured_llm = llm.with_structured_output(BillingResponse)


    # chain = prompt | structured_llm
    # response = chain.invoke({"question": question})
    # print(response)

    #data Ingestion
    # ingest_billing_documents()

    # check semantic similarity from Vector DB
    # vector_store = get_vector_store()
    # response = vector_store.similarity_search("why my bill amount is high")
    # print(response)
    
    # retriever = get_billing_retriever()

    # documents = retriever.invoke(
    #     "Why is my bill higher this month?"
    # )
    # print(documents)
    # 
    chain = get_billing_chain()

    response = chain.invoke(
        "Why is my bill higher this month?"
    )

    print(response)



if __name__ == "__main__":
    main()