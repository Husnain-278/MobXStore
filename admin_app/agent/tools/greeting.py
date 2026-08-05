from langchain_core.tools import tool


@tool
def greeting() -> str:
    """
    Generate a friendly greeting for the Admin User.

    Use this tool whenever the user asks you to greet someone.
    """
    name = "Admin"
    
    return f"Hello {name}! 👋 I hope you're having a wonderful day."