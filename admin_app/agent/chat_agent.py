from .llm import llm_with_tools
from .memory import MemoryBuilder
from .tool_executor import ToolExecutor
from .types import AgentResponse


class ChatAgent:
    """
    Orchestrates the conversation between the user,
    the LLM, and available tools.
    """

    MAX_TOOL_ITERATIONS = 5

    def invoke(self, messages):
        history = MemoryBuilder.build(messages)

        for _ in range(self.MAX_TOOL_ITERATIONS):

            ai_message = llm_with_tools.invoke(history)

            # Final response
            if not ai_message.tool_calls:
                return AgentResponse(
                    ai_message=ai_message,
                )

            # Add the assistant tool request
            history.append(ai_message)

            # Execute tools
            tool_messages = ToolExecutor.execute(ai_message)

            # Add tool results
            history.extend(tool_messages)

            # Loop continues and calls the LLM again

        raise RuntimeError(
            f"Maximum tool iterations ({self.MAX_TOOL_ITERATIONS}) exceeded."
        )