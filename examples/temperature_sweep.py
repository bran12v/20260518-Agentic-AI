"""Send the SAME prompt at three temperatures, three runs each.

Watch how T=0.0 gives near-identical responses, T=0.7 gives controlled
variety, and T=1.5 gives wild variation — all from the same input.
This is the knob you set in production via the temperature= argument.
"""

# 0.0-2.0 vs 0.0-1.0 -> 1.0 = 0.5
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

PROMPT = "Give me a one-sentence opening for a story about a lighthouse keeper. Try to use only 40 tokens"

# 3 runs per temperature, 3 temperatures, 9 total calls. Cost is pennies.
for T in (1.9, 1.95, 2.0):
    print(f"\n--- temperature={T} ---")
    for run in range(1, 4):
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": PROMPT}],
            temperature=T,
            max_tokens=40,
        )
        print(f"  Run {run}: {response.choices[0].message.content.strip()}")