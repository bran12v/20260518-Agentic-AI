"""Our first LLM call

No prompt engineering, no state, no cleverness. Just one question in, one result out."""

import os
from dotenv import load_dotenv

load_dotenv()

# get our azure env variables
if os.environ.get("AZURE_OPENAI_API_KEY"):
    from openai import AzureOpenAI
    # our agent client reference
    client = AzureOpenAI(
        api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
        api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
    )
    model = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME")

    response = client.chat.completions.create( # LLM API call
        model=model,
        messages=[
            {
                "role": "user", # who?
                "content": "In one short sentence, what is a transformer neural network?" # prompt
            }
        ],
    )


    # print the answer
    print("------- Model Answered -------")
    print(response.choices[0].message.content)

    # Show what else came back with the response object
    print("\n --- About this call ---")
    print(f"model:      {response.model}")
    print(f"prompt tokens:      {response.usage.prompt_tokens}")
    print(f"completion tokens:      {response.usage.completion_tokens}")
    print(f"finish reason:          {response.choices[0].finish_reason}")