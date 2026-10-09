from .models import Candidate, ScoreBreakdown


def _count_terms(text: str, terms: list[str]) -> int:
    """Count how many distinct terms appear in the resume."""
    return sum(1 for term in terms if term in text)


def score_candidate(
    candidate: Candidate,
    github_score: int = 0
):
    """
    Deterministic fallback scorer.

    Maximum score:
        AI / Agentic / RAG       = 40
        Python / Backend        = 30
        Cloud / Full Stack      = 15
        GitHub                   = 10
        Engineering Depth        = 5
        --------------------------------
        Total                    = 100

    This scorer is used when the LLM analyzer is unavailable.
    """

    text = candidate.raw_text.lower()

    # ==========================================================
    # 1. AI / AGENTIC / RAG PROJECT DEPTH — 40 POINTS
    # ==========================================================

    ai = 0

    # Strong AI technologies / architecture
    strong_ai_terms = [
        "rag",
        "retrieval augmented generation",
        "retrieval-augmented generation",
        "langchain",
        "langgraph",
        "llamaindex",
        "google adk",
        "ai agent",
        "agentic ai",
        "multi-agent",
        "multi agent",
        "tool calling",
        "function calling",
        "vector search",
        "vector database",
        "vector db",
        "embeddings",
        "semantic search",
    ]

    strong_ai_count = _count_terms(
        text,
        strong_ai_terms
    )

    # Basic LLM / GenAI technologies
    llm_terms = [
        "llm",
        "large language model",
        "openai",
        "gemini",
        "generative ai",
        "genai",
    ]

    llm_count = _count_terms(
        text,
        llm_terms
    )

    # AI implementation / workflow evidence
    implementation_terms = [
        "retrieval",
        "embedding",
        "vector",
        "chunking",
        "document processing",
        "semantic search",
        "prompt engineering",
        "prompt template",
        "pipeline",
        "orchestration",
        "tool calling",
        "function calling",
        "memory",
        "evaluation",
        "reranking",
        "reranker",
        "query rewriting",
        "knowledge base",
        "document ingestion",
        "workflow",
    ]

    implementation_count = _count_terms(
        text,
        implementation_terms
    )

    # Backend / product implementation supporting AI
    ai_backend_terms = [
        "fastapi",
        "flask",
        "django",
        "api",
        "backend",
        "mongodb",
        "postgres",
        "redis",
        "docker",
    ]

    ai_backend_count = _count_terms(
        text,
        ai_backend_terms
    )

    # ----------------------------------------------------------
    # Base AI score
    # ----------------------------------------------------------

    if strong_ai_count > 0:

        # Strong architecture starts above simple LLM usage.
        ai = 12

        # Reward multiple meaningful AI concepts.
        ai += min(
            12,
            strong_ai_count * 3
        )

        # Reward actual implementation evidence.
        ai += min(
            10,
            implementation_count * 2
        )

        # Reward backend/product integration.
        ai += min(
            6,
            ai_backend_count * 2
        )

    elif llm_count > 0:

        # LLM/API usage without deeper architecture.
        ai = 8

        ai += min(
            8,
            implementation_count * 2
        )

        ai += min(
            4,
            ai_backend_count
        )

    else:
        ai = 0

    # ----------------------------------------------------------
    # Thin LLM/API wrapper penalty
    # ----------------------------------------------------------

    shallow_markers = [
        "chatbot using openai api",
        "simple chatbot",
        "basic chatbot",
        "used openai api",
        "openai api chatbot",
        "gemini api chatbot",
        "llm api integration",
    ]

    shallow_count = _count_terms(
        text,
        shallow_markers
    )

    # Meaningful implementation evidence.
    meaningful_markers = [
        "retrieval",
        "rag",
        "embedding",
        "vector search",
        "vector database",
        "vector db",
        "chunking",
        "document ingestion",
        "tool calling",
        "function calling",
        "agentic",
        "multi-agent",
        "orchestration",
        "evaluation",
        "reranking",
        "memory",
        "workflow",
    ]

    meaningful_count = _count_terms(
        text,
        meaningful_markers
    )

    if shallow_count > 0 and meaningful_count == 0:
        ai -= 10

    # Don't allow deterministic scorer to exceed the category.
    ai = max(
        0,
        min(40, ai)
    )

    # ==========================================================
    # 2. PYTHON / BACKEND ENGINEERING — 30 POINTS
    # ==========================================================

    backend = 0

    if "python" in text:
        backend += 12

    backend_terms = [
        ("fastapi", 6),
        ("django", 4),
        ("flask", 3),
        ("asyncio", 2),
        ("async", 2),
        ("postgres", 2),
        ("postgresql", 2),
        ("redis", 2),
        ("backend", 2),
        ("rest api", 2),
        ("restful api", 2),
        ("api development", 2),
    ]

    for term, points in backend_terms:
        if term in text:
            backend += points

    backend = min(
        30,
        backend
    )

    # ==========================================================
    # 3. CLOUD / FULL STACK / DEPLOYMENT — 15 POINTS
    # ==========================================================

    cloud = 0

    cloud_terms = [
        ("gcp", 5),
        ("google cloud", 5),
        ("docker", 4),
        ("aws", 3),
        ("azure", 3),
        ("react", 1),
        ("next.js", 1),
        ("nextjs", 1),
        ("deployment", 2),
        ("render", 1),
        ("vercel", 1),
    ]

    for term, points in cloud_terms:
        if term in text:
            cloud += points

    cloud = min(
        15,
        cloud
    )

    # ==========================================================
    # 4. ENGINEERING DEPTH — 5 POINTS
    # ==========================================================

    engineering = 0

    engineering_terms = [
        "testing",
        "pytest",
        "unit test",
        "integration test",
        "caching",
        "cache",
        "queue",
        "observability",
        "concurrency",
        "async",
        "failure handling",
        "error handling",
        "exception handling",
        "architecture",
        "modular architecture",
        "microservices",
        "modular monolith",
        "logging",
    ]

    engineering = min(
        5,
        _count_terms(
            text,
            engineering_terms
        )
    )

    # ==========================================================
    # 5. GITHUB — 10 POINTS
    # ==========================================================

    github = max(
        0,
        min(10, int(github_score))
    )

    # ==========================================================
    # FINAL BREAKDOWN
    # ==========================================================

    breakdown = ScoreBreakdown(
        ai_project_depth=ai,
        python_backend=backend,
        cloud_fullstack=cloud,
        github=github,
        engineering_depth=engineering,
    )

    total = (
        breakdown.ai_project_depth
        + breakdown.python_backend
        + breakdown.cloud_fullstack
        + breakdown.github
        + breakdown.engineering_depth
    )

    return breakdown, total