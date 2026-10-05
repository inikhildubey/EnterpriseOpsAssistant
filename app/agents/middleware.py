import json
import re
import uuid

from langchain_core.messages import AIMessage
from langchain.agents.middleware.types import AgentMiddleware, ModelResponse

# Matches a tool call the model wrote out as JSON text instead of issuing a
# real tool_call, e.g. `{"name": "get_payment", "parameters": {"customer_id": "..."}}`.
_INLINE_TOOL_CALL_RE = re.compile(
    r'\{\s*"name"\s*:\s*"(?P<name>[^"]+)"\s*,\s*"(?:parameters|arguments)"\s*:\s*(?P<args>\{.*?\})\s*\}',
    re.DOTALL,
)


class InlineToolCallRepairMiddleware(AgentMiddleware):
    """Repairs small local models (observed with llama3.2:3b) that sometimes
    write a tool call as JSON text in the message content instead of emitting
    a real tool_call, which otherwise makes create_agent's loop stop early
    (an AIMessage with no tool_calls is treated as the final answer).
    """

    def wrap_model_call(self, request, handler):
        response = handler(request)

        ai_message = response.result[-1]
        if not isinstance(ai_message, AIMessage) or ai_message.tool_calls:
            return response

        match = _INLINE_TOOL_CALL_RE.search(ai_message.content or "")
        if not match:
            return response

        try:
            args = json.loads(match.group("args"))
        except json.JSONDecodeError:
            return response

        tool_name = match.group("name")
        available_tool_names = {
            tool.name for tool in request.tools if hasattr(tool, "name")
        }
        if tool_name not in available_tool_names:
            return response

        repaired_message = AIMessage(
            content=ai_message.content,
            tool_calls=[
                {
                    "name": tool_name,
                    "args": args,
                    "id": f"repaired-{uuid.uuid4().hex}",
                    "type": "tool_call",
                }
            ],
        )

        return ModelResponse(
            result=[repaired_message],
            structured_response=response.structured_response,
        )
