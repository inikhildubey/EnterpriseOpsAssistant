from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(
    title="EnterpriseOpsAssistant API",
    description="API for billing, accounts, support, and refund approvals.",
    version="0.1.0",
)


class ChatRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=5000,
        description="The user's message",
    )


class ChatResponse(BaseModel):
    answer: str
    department: str | None = None


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    # We'll connect your existing LangGraph router in the next step.
    return {
        "answer": "HUrraayyy..API is working. LangGraph integration is the next step.",
        "department": None,
    }
