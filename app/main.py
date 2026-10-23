
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.graph.router import build_router_graph


app = FastAPI(
    title="EnterpriseOpsAssistant API",
    description="API for billing, accounts, support, and refunds.",
    version="0.1.0",
)

# Build once so the in-memory checkpointer is shared across requests.
graph = build_router_graph()


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=5000)
    thread_id: str | None = None

    # Optional business context; ordinary chat doesn't need these.
    customer_id: str | None = None
    invoice_id: str | None = None
    refund_amount: float | None = Field(default=None, gt=0)
    refund_reason: str | None = None


class ChatResponse(BaseModel):
    answer: str
    department: str | None = None
    thread_id: str
    pending_approval: bool = False
    approval_request: dict | None = None
    approval_status: str | None = None


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    thread_id = request.thread_id or str(uuid4())

    state = {
        "question": request.question,
        "customer_id": request.customer_id,
        "invoice_id": request.invoice_id,
        "refund_amount": request.refund_amount,
        "refund_reason": request.refund_reason,
    }

    # Remove optional values that weren't supplied.
    state = {
        key: value
        for key, value in state.items()
        if value is not None
    }
    # config = {
    #     "configurable": {"thread_id": thread_id}
    # }

    try:
        # result = graph.invoke(state, config=config)
        print("[DEBUG] About to invoke graph", flush=True)
        print(f"[DEBUG] Input state: {state}", flush=True)
        result = graph.invoke(
            state,
            config={
                "configurable": {"thread_id": thread_id},
                "recursion_limit": 10,
            },
        )
        print("[DEBUG] Graph invocation completed", flush=True)
        print(f"[DEBUG] Result keys: {list(result.keys())}", flush=True)
    except Exception as exc:
        print(exc)
        raise HTTPException(
            status_code=500,
            detail=f"Debug error: {type(exc).__name__}: {exc}",
        ) from exc

    interrupts = result.get("__interrupt__", [])
    pending_approval = bool(interrupts)

    approval_request = None
    if pending_approval:
        interrupt_value = getattr(interrupts[0], "value", None)
        if isinstance(interrupt_value, dict):
            approval_request = interrupt_value

    return ChatResponse(
        answer=result.get(
            "answer",
            "Your request is waiting for human approval."
            if pending_approval
            else "I couldn't generate a response.",
        ),
        department=result.get("department"),
        thread_id=thread_id,
        pending_approval=pending_approval,
        approval_request=approval_request,
        approval_status=result.get("approval_status"),
    )


from typing import Literal
from pydantic import BaseModel
from fastapi import HTTPException
from langgraph.types import Command


class RefundApprovalRequest(BaseModel):
    thread_id: str
    approved: bool


@app.post("/refund/approval")
def refund_approval(request: RefundApprovalRequest):
    config = {
        "configurable": {
            "thread_id": request.thread_id
        }
    }

    try:
        print(
            f"[DEBUG] Resuming refund workflow: "
            f"thread_id={request.thread_id}, approved={request.approved}",
            flush=True,
        )

        result = graph.invoke(
            Command(resume={"approved": request.approved}),
            config=config,
        )

        print(f"[DEBUG] Resume result: {result}", flush=True)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Approval processing failed: {type(exc).__name__}: {exc}",
        ) from exc

    interrupts = result.get("__interrupt__", [])
    pending_approval = bool(interrupts)

    return {
        "answer": result.get("answer", ""),
        "thread_id": request.thread_id,
        "pending_approval": pending_approval,
        "approval_request": (
            getattr(interrupts[0], "value", None)
            if pending_approval
            else None
        ),
        "approval_status": result.get("approval_status"),
    }
