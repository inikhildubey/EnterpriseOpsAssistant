from langchain_core.prompts import ChatPromptTemplate


prompt = ChatPromptTemplate.from_template(
    """
    You are a helpful billing assistant.
    Answer the user's question clearly and concisely.

    User question:
    {question}
    """
)