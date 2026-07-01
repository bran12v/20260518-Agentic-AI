"""Azure Open AI Embeddings File.

Functions for the use of embedding chunks into vector DB.

Embedding dimensions (1536 - text-embedding-3-small) MUST match the 'vector(n)' column dimension.
Make sure to swap dimension if the underlying embedding model changes. (Ex. 3-large: 3072 dims)
"""

from openai import AzureOpenAI
import os
from functools import lru_cache

EMBEDDING_DIMENSIONS = 1536


@lru_cache(maxsize=1)
def _client() -> AzureOpenAI:
    """Single client per process. Reused across requests."""
    return AzureOpenAI(
        api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
        api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
    )

def _deployment() -> str:
    return os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")

def embed_text(text: str) -> list[float]:
    """Embed a single string. Returns a 1536-dim vector."""
    response = _client().embeddings.create(model=_deployment(), input=text)
    return response.data[0].embedding

def embed_batch(texts: list[str]) -> list[list[float]]:
    """Embed a batch in one request. Azure caps the request body so we will need to
    size our batches effectively."""
    if not texts:
        return []
    response = _client().embeddings.create(model=_deployment(), input=texts)
    return [item.embedding for item in response.data] # [[1,2,3], [3,4,2], [1,7,3]] An array of embeddings (vector arrays)