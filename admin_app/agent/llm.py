import os

from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI

from .tools import TOOLS

load_dotenv()

MODEL_NAME = os.getenv(
    "MISTRAL_MODEL",
    "mistral-small-2506",
)

TEMPERATURE = float(
    os.getenv("MISTRAL_TEMPERATURE", "0.3")
)

llm = ChatMistralAI(
    model=MODEL_NAME,
    api_key=os.getenv("MISTRAL_API_KEY"),
    temperature=TEMPERATURE,
)

llm_with_tools = llm.bind_tools(TOOLS)