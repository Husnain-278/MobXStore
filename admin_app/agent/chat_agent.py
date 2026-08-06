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

    def stream(self, messages):
        """Stream an agent response, including any intermediate tool calls.

        The yielded dictionaries are deliberately transport-agnostic.  The view
        turns them into Server-Sent Events, which keeps the agent usable from
        non-HTTP callers as well.
        """
        history = MemoryBuilder.build(messages)

        for _ in range(self.MAX_TOOL_ITERATIONS):
            response = None

            for chunk in llm_with_tools.stream(history):
                response = chunk if response is None else response + chunk

                # Tool-call chunks do not contain user-visible text.  Only
                # forward actual text deltas to the client.
                if chunk.content:
                    yield {
                        "type": "content.delta",
                        "delta": self._content_as_text(chunk.content),
                    }

            if response is None:
                raise RuntimeError("The LLM returned an empty stream.")

            if not response.tool_calls:
                yield {
                    "type": "response.completed",
                    "ai_message": response,
                }
                return

            history.append(response)

            for tool_call in response.tool_calls:
                yield {
                    "type": "tool.call",
                    "id": tool_call["id"],
                    "name": tool_call["name"],
                    "input": tool_call["args"],
                }

                tool_message = ToolExecutor.execute_call(tool_call)
                yield {
                    "type": "tool.result",
                    "id": tool_call["id"],
                    "name": tool_call["name"],
                    "output": tool_message.content,
                }
                history.append(tool_message)

        raise RuntimeError(
            f"Maximum tool iterations ({self.MAX_TOOL_ITERATIONS}) exceeded."
        )

    @staticmethod
    def _content_as_text(content):
        """Normalise LangChain's string or structured content blocks."""
        if isinstance(content, str):
            return content

        if isinstance(content, list):
            return "".join(
                block.get("text", "") if isinstance(block, dict) else str(block)
                for block in content
            )

        return str(content)
