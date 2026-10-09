PYTHON_TERMS = {
    "python",
    "python3",
    "fastapi",
    "django",
    "flask",
    "pandas",
    "numpy",
    "scikit-learn",
    "tensorflow",
    "pytorch",
}

# Strong evidence of actual AI/LLM/RAG/agentic implementation
STRONG_AI_TERMS = {
    "rag",
    "retrieval augmented generation",
    "retrieval-augmented generation",
    "langchain",
    "langgraph",
    "llamaindex",
    "google adk",
    "embeddings",
    "vector search",
    "vector database",
    "vector db",
    "ai agent",
    "agentic ai",
    "multi-agent",
    "multi agent",
    "tool calling",
    "function calling",
    "semantic search",
}

# These alone should NOT be enough for AI eligibility.
WEAK_AI_TERMS = {
    "llm",
    "large language model",
    "openai",
    "gemini",
    "genai",
    "generative ai",
}


def _contains_term(text: str, terms: set[str]) -> bool:
    text = text.lower()
    return any(term in text for term in terms)


def check_eligibility(resume_text: str):
    """
    Hard eligibility check.

    Candidate must have:
        1. Genuine Python evidence
        2. Meaningful AI / LLM / RAG / Agentic evidence

    Weak mentions such as only 'OpenAI' or 'Gemini'
    are not sufficient by themselves.
    """

    text = resume_text.lower()

    # --------------------------------------------------
    # Python requirement
    # --------------------------------------------------

    python_found = _contains_term(
        text,
        PYTHON_TERMS
    )

    # --------------------------------------------------
    # Strong AI requirement
    # --------------------------------------------------

    strong_ai_found = _contains_term(
        text,
        STRONG_AI_TERMS
    )

    # --------------------------------------------------
    # Weak AI evidence
    # --------------------------------------------------

    weak_ai_found = _contains_term(
        text,
        WEAK_AI_TERMS
    )

    # --------------------------------------------------
    # Meaningful AI evidence
    #
    # Strong AI terms are sufficient.
    #
    # Alternatively, multiple weak AI concepts
    # together can indicate actual AI work.
    # --------------------------------------------------

    meaningful_ai = strong_ai_found

    # Example:
    # "LLM + embeddings"
    # "OpenAI + vector database"
    # etc.
    weak_terms_found = [
        term
        for term in WEAK_AI_TERMS
        if term in text
    ]

    meaningful_ai = (
        meaningful_ai
        or len(weak_terms_found) >= 2
    )

    # --------------------------------------------------
    # Rejection reasons
    # --------------------------------------------------

    reasons = []

    if not python_found:
        reasons.append(
            "No evidence of Python stack"
        )

    if not meaningful_ai:
        reasons.append(
            "No meaningful AI/LLM/RAG/agentic project evidence"
        )

    # --------------------------------------------------
    # Final decision
    # --------------------------------------------------

    eligible = (
        python_found
        and meaningful_ai
    )

    return eligible, reasons