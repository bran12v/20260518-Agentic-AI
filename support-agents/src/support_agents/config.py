"""Set up the Environment Loading and OpenAI client factory for support-agents."""

import os

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