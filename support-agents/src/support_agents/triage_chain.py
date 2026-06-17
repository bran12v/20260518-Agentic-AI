"""LCEL version of the triage classifier."""

import warnings

import re

from langchain_core.runnables import Runnable, RunnableLambda, RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from support_agents.config import langchain_chat_model

from support_agents.triage import TriageSuggestion

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic.main")
"""
Hello.
asdasfafa

--

From, Brandon
"""
# Preprocessing step
def _strip_signature(body: str) -> str:
    """Trim email signatures and quoted reply blocks before classification of tickets.
    Customer emails typically include "On Mon at 10:03 AM, support@example.com
    wrote:" quote blocks and "-- <signature>" footers that add tokens without
    adding signal.
    """
    body = re.split(r"\n-{2,}\s*\n", body, maxsplit=1)[0]
    body = re.split(r"\nOn .+ wrote:\n", body, maxsplit=1)[0]
    return body.strip()

_PREP = RunnableLambda(lambda d: {"body": _strip_signature(d["body"])})

_CLASSIFY_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a triage assistant for a customer-support platform"),
        ("human", "Triage this inbound ticket: \n\n{body}")
    ]
)

_DRAFT_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You draft a brief, empathetic first reply to a customer ticket. "
            "Just 2-3 sentances. No commitments on pricing, no timelines, no refunds -"
            "just acknowledge and state the next step."
        ),
        ("human", "{body}")
    ]
)

def build_classifier_chain() -> Runnable: # factory function
    """Typed classifier: body -> TriageSuggestion
    uses 'method='json_schema', strict=True' so azure will hard enforce the schema at
    the API boundary before the model returns."""
    model = langchain_chat_model().with_structured_output(
        TriageSuggestion, method="json_schema", strict=True
    )
    return _PREP | _CLASSIFY_PROMPT | model

def build_triage_chain() -> Runnable:
    """
    classification + draft reply, running in parallel.
    """
    classify = build_classifier_chain()
    draft = _PREP | _DRAFT_PROMPT | langchain_chat_model()
    return RunnableParallel(classification=classify, draft_reply=draft)

if __name__ == "__main__":
    from support_agents.triage import TKT_10001_BODY 

    # chain = build_classifier_chain()
    # result: TriageSuggestion = chain.invoke({"body": TKT_10001_BODY})
    # print(f"category:           {result.category}")
    # print(f"priority:           {result.priority}")
    # print(f"summary:            {result.summary}")
    # print(f"suggest_team:       {result.suggest_team}")

    chain = build_triage_chain()
    result = chain.invoke({"body": TKT_10001_BODY})
    tr: TriageSuggestion = result["classification"]
    draft: str = result["draft_reply"]
    print(f"category:           {tr.category}")
    print(f"priority:           {tr.priority}")
    print(f"summary:            {tr.summary}")
    print(f"suggest_team:       {tr.suggest_team}")
    print(f"\ndraft reply:\n{draft.content}")
    