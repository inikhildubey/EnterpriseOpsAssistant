from app.models.factory import get_llm
from app.prompts.billing import prompt


llm = get_llm()
def main():
    question = "why my bill amount is high"

    # formatted_prompt = prompt.invoke({
    #     "question": question
    # })    
    # response = llm.invoke(formatted_prompt)

    chain = prompt | llm
    response = chain.invoke({"question": question})

    print(response.content)


if __name__ == "__main__":
    main()