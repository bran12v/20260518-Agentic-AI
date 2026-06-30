"""Token-bounded chunking

Why chunk at all? - Embedding models have a token cap

Why token-aware? - If we split on character count or sentance count
    that will drift away from how the underlying model actually
    views the data. We want to structure ourselves in the same
    way the data will be consumed.

Overlap matters because context may be lost between chunks.
"""

import tiktoken

# cl100k_base is the encoding model for the gpt-3.5-turbo, gpt-4 families.
_ENCODING = tiktoken.get_encoding("cl100k_base")

def chunk_text(
    text: str,
    chunk_tokens: int = 500,
    overlap_tokens: int = 50
) -> list[str]:
    """Split text into token-bounded chunks w/ overlap.
    
    Returns a list of chunk strings. 
    
    defaults to 500 chunk size w/ 50 token overlap.
    """
    if not text.strip():
        return []
    if chunk_tokens <= 0:
        raise ValueError(f"chunk_tokens must be positive, got {chunk_tokens}")
    if overlap_tokens < 0 or overlap_tokens >= chunk_tokens:
        raise ValueError(f"overlap_tokens must be in [0, chunk_tokens), got {overlap_tokens}")
    
    tokens = _ENCODING.encode(text)
    if (len(tokens) <= chunk_tokens):
        return [text]
    
    step = chunk_tokens - overlap_tokens # 500-50 = 450
    chunks: list[str] = []
    start = 0
    while start < len(tokens):
        end = min(start + chunk_tokens, len(tokens)) # 450 + 50 = 500, 
        chunks.append(_ENCODING.decode(tokens[start:end])) # 0, 50
        if end >= len(tokens):
            break
        start += step # 450
    return chunks

def count_tokens(text: str) -> int:
    """Token count under cl100k_base - useful for test"""
    return len(_ENCODING.encode(text))

# 2 * 200 = 400 tokens
# chunk size = 50
# overlap = 10