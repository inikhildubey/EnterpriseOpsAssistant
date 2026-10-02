from pydantic import BaseModel, Field


class BillingResponse(BaseModel):
    answer: str = Field(
        description="Clear answer to the user's billing question"
    )

    confidence: float = Field(
        ge=0,
        le=1,
        description="Confidence in the answer, from 0 to 1"
    )

    # sources: list[str] = Field(
    #     default_factory=list,
    #     description="Sources supporting the answer"
    # )

    requires_human: bool = Field(
        default=False,
        description="Whether the request requires human intervention"
    )