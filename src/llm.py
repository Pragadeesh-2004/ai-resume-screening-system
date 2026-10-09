"""Optional LLM adapter.

The core screening pipeline does not depend on an LLM. If a provider is configured,
this module can be extended to return structured Pydantic data. Keeping this adapter
isolated makes provider replacement easy and ensures an LLM failure does not stop a batch.
"""


def enrich_with_llm(candidate):
    return candidate
