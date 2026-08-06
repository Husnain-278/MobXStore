from .greeting import greeting
from .streaming_test import streaming_test

TOOLS = [
    greeting,
    streaming_test,
]

TOOL_MAP = {
    tool.name: tool
    for tool in TOOLS
}

__all__ = [
    "TOOLS",
    "TOOL_MAP",
]
