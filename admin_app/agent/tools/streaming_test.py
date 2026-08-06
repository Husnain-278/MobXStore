from langchain_core.tools import tool


@tool
def streaming_test(message: str = "streaming is working") -> str:
    """Return a deterministic result to verify streamed tool-call events.

    Use this only when the user explicitly asks to test streaming tools or to
    run the streaming test tool.
    """
    return f"Streaming tool completed successfully: {message}"
