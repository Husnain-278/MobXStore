from .greeting import greeting

TOOLS = [
    greeting,
]

TOOL_MAP = {
    tool.name: tool
    for tool in TOOLS
}

__all__ = [
    "TOOLS",
    "TOOL_MAP",
]