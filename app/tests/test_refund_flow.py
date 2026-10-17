
from langgraph.types import Command
from app.graph.router import build_router_graph

graph = build_router_graph()

config = {
    "configurable": {"thread_id": "refund-test-001"}
}

# Start the refund workflow
result = graph.invoke(
    {
        "question": "I want to request a refund",
        "customer_id": "CUST-1001",
        "invoice_id": "INV-12345",
        "refund_amount": 249.0,
        "refund_reason": "Incorrect charge",
    },
    config=config,
)

print("INITIAL RESULT:")
print(result)

# # Resume only if the graph paused for approval
# if result.get("__interrupt__"):
#     result = graph.invoke(
#         Command(resume={"approved": True}),
#         config=config,
#     )
#     print("RESUMED RESULT:")
#     print(result)
# else:
#     print("No interrupt detected. Inspect the initial result.")

if result.get("__interrupt__"):
    decision = input("Approve this refund? (yes/no): ").strip().lower()

    result = graph.invoke(
        Command(resume={"approved": decision == "yes"}),
        config=config,
    )

    print("RESUMED RESULT:")
    print(result)