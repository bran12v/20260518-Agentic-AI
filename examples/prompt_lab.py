"""We are going to implement 3 prompt styles: zero-shot, few-shot, role and format"""

import os
from dotenv import load_dotenv
load_dotenv()

if os.environ.get("AZURE_OPENAI_API_KEY"):
    from openai import AzureOpenAI
    client = AzureOpenAI(
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_version=os.environ["AZURE_OPENAI_API_VERSION"],
    )
    model = os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"]

# Three prompts, increasing in sophistication. None = no system prompt.
PROMPTS = {
    "V1 zero-shot":   None,
    "V2 role+format": "You are a senior contracts analyst. In one sentence under 20 words, identify the single highest-risk element.",
    "V3 few-shot":    (
        "You are a senior contracts analyst. In one sentence under 20 words, identify the single highest-risk element.\n"
        "Evaluate examples dependent on the analysis reached."
        "A risk is defined as something that would impede the progress of a project or compromise it entirely. "
        "If a risk cannot be identified mark it as undefined. Replace the [...] with the noted risk."
        "Example: [...] -> [risk] is an [analysis conclusion] performance standard."
    ),
}

TESTS = [
    ("Contractor shall use comercially reasonable efforts to deliver", "undefined"),
    ("Payment due within 90 days of invoice.", "cash flow"),
    ("Governed by the laws of a fictional state.", "jurisdiction")
]

for label, system in PROMPTS.items():
    print(f"\n=== {label} ===")
    hits = 0
    for clause, keyword in TESTS:
        messages = [{"role": "user", "content": clause}]
        if system:
            messages.insert(0, {"role": "system", "content": system}) 
        answer = client.chat.completions.create(
            model=model, messages=messages, temperature=0, max_tokens=60
        ).choices[0].message.content.strip()
        hit = keyword.lower() in answer.lower()
        if hit: hits += 1
        print(f"    [{'PASS' if hit else 'FAIL'}] keyword='{keyword}' | '{answer}'")
    print(f"    score: {hits}/{len(TESTS)}")




"""
API1
[
{"role": "system", "content": system},
{"role": "user", "content": TEST1}
]
API2
[
{"role": "system", "content": system},
{"role": "user", "content": TEST2}
]
API3
[
{"role": "system", "content": system},
{"role": "user", "content": TEST3}
]
"""