"""Set up the Environment Loading and OpenAI client factory for support-agents."""

import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()

def openai_client():
    """Return an OpenAI-compatible client."""
    if os.environ.get("AZURE_OPENAI_API_KEY"):
        from openai import AzureOpenAI

        return AzureOpenAI(
            api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
        )

MODEL = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME")

def langchain_chat_model(temperature: float = 0.0, **kwargs: Any):
    """Return a langchain 'ChatModel' configured for Azure."""
    if os.environ.get("AZURE_OPENAI_API_KEY"):
        from langchain_openai import AzureChatOpenAI

        return AzureChatOpenAI(
            api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
            azure_deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME"),
            temperature=temperature,
            **kwargs
        )

    # fallback plan if we dont have azure, use normal openai (We will never hit this code)
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(model="gpt-4o-mini", temperature=temperature, **kwargs)
    