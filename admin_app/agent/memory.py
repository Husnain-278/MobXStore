from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)

from .prompts import SYSTEM_PROMPT
from admin_app.models import Message


class MemoryBuilder:
    """
    Convert database messages into LangChain messages.
    """

    @staticmethod
    def build(messages):
        """
        Build LangChain conversation history.

        Args:
            messages: Iterable of Message model instances.

        Returns:
            list[BaseMessage]
        """
        history = [
            SystemMessage(content=SYSTEM_PROMPT)
        ]

        for message in messages:

            if message.role == Message.Role.USER:
                history.append(
                    HumanMessage(content=message.content)
                )

            elif message.role == Message.Role.ASSISTANT:
                history.append(
                    AIMessage(content=message.content)
                )


        return history