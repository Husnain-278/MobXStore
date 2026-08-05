from dataclasses import dataclass

from langchain_core.messages import AIMessage


@dataclass(slots=True)
class AgentResponse:
    ai_message: AIMessage