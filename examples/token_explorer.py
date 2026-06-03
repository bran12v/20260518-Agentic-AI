"""Encode various texts with tiktoken and print the tokens with their IDs.

tiktoken ships the exact BPE tokenizer used by OpenAI models. For GPT-4o
the encoding is called 'o200k_base' and has about 200,000 entries.
"""
import tiktoken

# Pick the encoder matching the model we care about.
# 'o200k_base' is GPT-4o. 'cl100k_base' is GPT-3.5 / GPT-4.
enc = tiktoken.encoding_for_model("gpt-4o")


def show(label: str, text: str) -> None:
    tokens = enc.encode(text)
    print(f"\n--- {label} ({len(tokens)} tokens, {len(text)} chars) ---") # label is the type of "prose"
    for tid in tokens:
        # decode_single_token_bytes returns bytes; use errors='replace' so
        # multi-byte characters (emoji, Japanese) don't crash when a single
        # token is only part of a UTF-8 sequence.
        piece = enc.decode_single_token_bytes(tid).decode("utf-8", errors="replace")
        print(f"  {tid:>6}  {piece!r}")


if __name__ == "__main__":
    show("English prose", "Hello, how are you today?")
    show("JSON", '{"user": "alice", "age": 30}')
    show("Python code", "def add(a: int, b: int) -> int:\n    return a + b")
    show("Japanese", "こんにちは、元気ですか？")
    show("Emoji",     "Let's celebrate! 🎉🎊🎈")