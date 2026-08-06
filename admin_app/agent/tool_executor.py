from langchain_core.messages import ToolMessage

from .tools import TOOL_MAP


class ToolExecutor:
    """
    Executes tool calls requested by the LLM.
    """

    @staticmethod
    def execute(ai_message):
        return [
            ToolExecutor.execute_call(tool_call)
            for tool_call in ai_message.tool_calls
        ]

    @staticmethod
    def execute_call(tool_call):
        """Execute one call so streaming can report its lifecycle in order."""
        tool = TOOL_MAP[tool_call["name"]]
        result = tool.invoke(tool_call["args"])

        return ToolMessage(
            content=str(result),
            tool_call_id=tool_call["id"],
            name=tool_call["name"],
        )
