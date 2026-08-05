from langchain_core.messages import ToolMessage

from .tools import TOOL_MAP


class ToolExecutor:
    """
    Executes tool calls requested by the LLM.
    """

    @staticmethod
    def execute(ai_message):
        tool_messages = []

        for tool_call in ai_message.tool_calls:

            tool = TOOL_MAP[tool_call["name"]]

            result = tool.invoke(tool_call["args"])

            tool_messages.append(
                ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call["id"],
                    name=tool_call["name"],
                )
            )

        return tool_messages