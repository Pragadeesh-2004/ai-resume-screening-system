import hashlib
import os
import time
from pathlib import Path
from typing import List

from .parser import extract_resume_text
from .extractor import extract_candidate
from .eligibility import check_eligibility
from .github import enrich_github
from .scorer import score_candidate
from .models import CandidateResult, BatchSummary, ScreeningOutput


# ============================================================
# Helper functions
# ============================================================

def _fallback_evidence(text: str) -> List[str]:
    """
    Extract concrete evidence from the resume when Gemini
    is unavailable.
    """

    text_lower = text.lower()
    evidence = []

    evidence_terms = [
        ("RAG", [
            "rag",
            "retrieval augmented generation",
            "retrieval-augmented generation",
        ]),
        ("LangChain", ["langchain"]),
        ("LangGraph", ["langgraph"]),
        ("LlamaIndex", ["llamaindex"]),
        ("AI agents", [
            "ai agent",
            "agentic ai",
            "agentic",
            "multi-agent",
            "multi agent",
        ]),
        ("Embeddings", ["embedding", "embeddings"]),
        ("Vector search", ["vector search"]),
        ("Vector database", [
            "vector database",
            "vector db",
        ]),
        ("Semantic search", ["semantic search"]),
        ("Tool/function calling", [
            "tool calling",
            "function calling",
        ]),
        ("Document processing", [
            "document ingestion",
            "document processing",
            "document extraction",
        ]),
        ("Evaluation", [
            "evaluation",
            "evaluation pipeline",
        ]),
        ("Python", ["python", "python3"]),
        ("FastAPI", ["fastapi"]),
        ("Django", ["django"]),
        ("Flask", ["flask"]),
        ("Docker", ["docker"]),
        ("AWS", ["aws"]),
        ("Azure", ["azure"]),
        ("GCP", ["gcp", "google cloud"]),
    ]

    for label, terms in evidence_terms:
        if any(term in text_lower for term in terms):
            evidence.append(label)

    return evidence[:10]


def _fallback_project_summary(candidate, text: str) -> str:
    """
    Produce a useful project summary without an LLM.
    """

    if candidate.projects:
        project_descriptions = []

        for project in candidate.projects[:2]:
            name = project.name.strip()
            description = project.description.strip()

            if name and description:
                project_descriptions.append(
                    f"{name}: {description}"
                )
            elif description:
                project_descriptions.append(description)
            elif name:
                project_descriptions.append(name)

        if project_descriptions:
            return " | ".join(project_descriptions)

    text_lower = text.lower()

    if "rag" in text_lower:
        return (
            "Resume contains evidence of a RAG-based "
            "AI implementation."
        )

    if "langgraph" in text_lower:
        return (
            "Resume contains evidence of an agentic AI "
            "workflow using LangGraph."
        )

    if "langchain" in text_lower:
        return (
            "Resume contains evidence of an AI application "
            "using LangChain."
        )

    if "agentic" in text_lower or "ai agent" in text_lower:
        return (
            "Resume contains evidence of an AI agent or "
            "agentic workflow."
        )

    if (
        "embedding" in text_lower
        or "vector search" in text_lower
    ):
        return (
            "Resume contains evidence of semantic retrieval "
            "or embedding-based AI implementation."
        )

    return (
        "AI-related implementation evidence detected "
        "in resume."
    )


def _fallback_strengths(candidate, breakdown) -> List[str]:
    """
    Generate evidence-based strengths when Gemini is unavailable.
    """

    strengths = []
    text = candidate.raw_text.lower()

    # AI strengths
    if "rag" in text:
        strengths.append(
            "Hands-on RAG implementation evidence"
        )

    elif "langgraph" in text:
        strengths.append(
            "Agentic workflow implementation using LangGraph"
        )

    elif "langchain" in text:
        strengths.append(
            "Practical LLM application development using LangChain"
        )

    elif "agentic" in text or "ai agent" in text:
        strengths.append(
            "AI agent or agentic workflow experience"
        )

    elif (
        "embedding" in text
        or "vector search" in text
        or "vector database" in text
    ):
        strengths.append(
            "Embedding or vector-based retrieval experience"
        )

    # Python/backend strengths
    if "python" in text:
        if "fastapi" in text:
            strengths.append(
                "Python backend development with FastAPI"
            )
        elif "django" in text:
            strengths.append(
                "Python backend development with Django"
            )
        elif "flask" in text:
            strengths.append(
                "Python backend development with Flask"
            )
        else:
            strengths.append(
                "Strong Python development evidence"
            )

    # Cloud/deployment
    cloud_terms = [
        "aws",
        "azure",
        "gcp",
        "google cloud",
        "docker",
        "deployment",
    ]

    if any(term in text for term in cloud_terms):
        strengths.append(
            "Cloud or deployment experience"
        )

    # GitHub
    if breakdown.github >= 6:
        strengths.append(
            "Strong public GitHub activity"
        )
    elif breakdown.github > 0:
        strengths.append(
            "Public GitHub activity detected"
        )

    # Engineering
    if breakdown.engineering_depth >= 4:
        strengths.append(
            "Evidence of engineering practices such as "
            "testing, caching, architecture, or error handling"
        )

    return strengths[:5]


def _fallback_concerns(candidate, breakdown, github_status) -> List[str]:
    """
    Generate useful concerns when Gemini is unavailable.
    """

    concerns = []
    text = candidate.raw_text.lower()

    # AI concerns
    if breakdown.ai_project_depth < 20:
        concerns.append(
            "Limited depth of AI project implementation evidence"
        )

    # Thin wrapper detection
    shallow_markers = [
        "simple chatbot",
        "basic chatbot",
        "openai api chatbot",
        "gemini api chatbot",
        "used openai api",
        "llm api integration",
    ]

    meaningful_markers = [
        "rag",
        "retrieval",
        "embedding",
        "vector",
        "chunking",
        "agentic",
        "tool calling",
        "function calling",
        "multi-agent",
        "workflow",
        "evaluation",
        "reranking",
    ]

    shallow = any(
        marker in text
        for marker in shallow_markers
    )

    meaningful = any(
        marker in text
        for marker in meaningful_markers
    )

    if shallow and not meaningful:
        concerns.append(
            "AI experience appears focused on relatively thin "
            "LLM/API integration"
        )

    # Python/backend concerns
    if breakdown.python_backend < 15:
        concerns.append(
            "Limited Python/backend engineering evidence"
        )

    # Cloud
    if breakdown.cloud_fullstack < 5:
        concerns.append(
            "Limited cloud or deployment evidence"
        )

    # GitHub
    if github_status == "error":
        concerns.append(
            "GitHub enrichment unavailable"
        )

    return concerns[:5]


def _safe_int(value, default=0):
    """
    Safely convert an LLM value into an integer.
    """

    try:
        return int(value)
    except (TypeError, ValueError):
        return default


# ============================================================
# Main screening pipeline
# ============================================================

def screen_directory(
    input_dir: str,
    llm_analyzer=None
) -> ScreeningOutput:

    start_time = time.perf_counter()

    input_path = Path(input_dir)

    if not input_path.exists():
        raise FileNotFoundError(
            f"Input directory does not exist: {input_dir}"
        )

    if not input_path.is_dir():
        raise NotADirectoryError(
            f"Input path is not a directory: {input_dir}"
        )

    # ========================================================
    # Discover supported resume formats
    # ========================================================

    supported_extensions = {
        ".pdf",
        ".docx",
        ".txt",
    }

    paths = sorted(
        path
        for path in input_path.iterdir()
        if (
            path.is_file()
            and path.suffix.lower() in supported_extensions
        )
    )

    summary = BatchSummary(
        total_resumes=len(paths)
    )

    results: List[CandidateResult] = []

    # Duplicate detection
    seen_hashes = set()

    # GitHub API token
    github_token = os.getenv("GITHUB_TOKEN")

    total_files = len(paths)

    print()
    print("==============================================")
    print("       AI RESUME SCREENING PIPELINE")
    print("==============================================")
    print(f"Input directory : {input_dir}")
    print(f"Resumes found   : {total_files}")
    print(
        f"Gemini          : "
        f"{'Enabled' if llm_analyzer else 'Fallback only'}"
    )
    print("==============================================")
    print()

    # ========================================================
    # Process resumes
    # ========================================================

    for index, path in enumerate(paths, start=1):

        print(
            f"[{index}/{total_files}] "
            f"{path.name}"
        )

        try:

            # ------------------------------------------------
            # 1. Text extraction
            # ------------------------------------------------

            text = extract_resume_text(path)

            if not text.strip():
                raise ValueError(
                    "Resume contains no extractable text"
                )

            # ------------------------------------------------
            # 2. Duplicate detection
            # ------------------------------------------------

            fingerprint = hashlib.sha256(
                text.strip().encode("utf-8")
            ).hexdigest()

            if fingerprint in seen_hashes:

                print(
                    "    → Duplicate resume skipped"
                )

                continue

            seen_hashes.add(fingerprint)

            summary.successfully_parsed += 1

            # ------------------------------------------------
            # 3. Extract candidate information
            # ------------------------------------------------

            candidate = extract_candidate(text)

            # ------------------------------------------------
            # 4. HARD ELIGIBILITY
            # ------------------------------------------------

            eligible, rejection_reasons = (
                check_eligibility(text)
            )

            # ------------------------------------------------
            # Rejected candidate
            # ------------------------------------------------

            if not eligible:

                summary.rejected += 1

                results.append(
                    CandidateResult(
                        candidate_name=candidate.name,
                        eligible=False,
                        rejection_reasons=rejection_reasons,
                        matched_skills=candidate.skills,
                        analysis_method="not_analyzed",
                        source_file=path.name,
                    )
                )

                print(
                    "    → REJECTED"
                )

                if rejection_reasons:
                    for reason in rejection_reasons:
                        print(
                            f"       Reason: {reason}"
                        )

                print()

                continue

            # ------------------------------------------------
            # Eligible candidate
            # ------------------------------------------------

            summary.eligible += 1

            # ------------------------------------------------
            # 5. GitHub enrichment
            # ------------------------------------------------

            try:

                gh = enrich_github(
                    candidate.github_url,
                    github_token
                )

            except Exception as github_error:

                # GitHub failure must NEVER fail screening.

                print(
                    f"    → GitHub enrichment failed: "
                    f"{github_error}"
                )

                gh = {
                    "score": 0,
                    "summary": (
                        "GitHub enrichment unavailable"
                    ),
                    "status": "error",
                }

            # ------------------------------------------------
            # 6. Deterministic fallback score
            # ------------------------------------------------

            breakdown, total = score_candidate(
                candidate,
                gh.get("score", 0)
            )

            # ------------------------------------------------
            # 7. Initialize fallback information
            # ------------------------------------------------

            candidate_name = candidate.name

            project_summary = _fallback_project_summary(
                candidate,
                text
            )

            strengths = _fallback_strengths(
                candidate,
                breakdown
            )

            concerns = _fallback_concerns(
                candidate,
                breakdown,
                gh.get("status")
            )

            evidence = _fallback_evidence(text)

            analysis_method = "rule_based_fallback"

            # ------------------------------------------------
            # 8. Gemini semantic analysis
            # ------------------------------------------------

            if llm_analyzer is not None:

                print(
                    "    → Gemini analyzing..."
                )

                try:

                    llm_result = (
                        llm_analyzer.analyze(text)
                    )

                    # ----------------------------------------
                    # Candidate name
                    # ----------------------------------------

                    llm_name = llm_result.get(
                        "candidate_name",
                        ""
                    )

                    if (
                        isinstance(llm_name, str)
                        and llm_name.strip()
                        and llm_name.strip().lower()
                        not in {
                            "unknown",
                            "unknown candidate",
                        }
                    ):
                        candidate_name = (
                            llm_name.strip()
                        )

                    # ----------------------------------------
                    # Project summary
                    # ----------------------------------------

                    llm_project_summary = (
                        llm_result.get(
                            "project_summary",
                            ""
                        )
                    )

                    if (
                        isinstance(
                            llm_project_summary,
                            str
                        )
                        and llm_project_summary.strip()
                    ):
                        project_summary = (
                            llm_project_summary.strip()
                        )

                    # ----------------------------------------
                    # LLM scores
                    # ----------------------------------------

                    ai_score = _safe_int(
                        llm_result.get(
                            "ai_project_depth",
                            breakdown.ai_project_depth
                        ),
                        breakdown.ai_project_depth
                    )

                    python_score = _safe_int(
                        llm_result.get(
                            "python_backend",
                            breakdown.python_backend
                        ),
                        breakdown.python_backend
                    )

                    cloud_score = _safe_int(
                        llm_result.get(
                            "cloud_fullstack",
                            breakdown.cloud_fullstack
                        ),
                        breakdown.cloud_fullstack
                    )

                    engineering_score = _safe_int(
                        llm_result.get(
                            "engineering_depth",
                            breakdown.engineering_depth
                        ),
                        breakdown.engineering_depth
                    )

                    # ----------------------------------------
                    # Clamp scores to assignment limits
                    # ----------------------------------------

                    ai_score = max(
                        0,
                        min(40, ai_score)
                    )

                    python_score = max(
                        0,
                        min(30, python_score)
                    )

                    cloud_score = max(
                        0,
                        min(15, cloud_score)
                    )

                    engineering_score = max(
                        0,
                        min(5, engineering_score)
                    )

                    # GitHub always stays deterministic
                    github_score = max(
                        0,
                        min(
                            10,
                            _safe_int(
                                breakdown.github,
                                0
                            )
                        )
                    )

                    # ----------------------------------------
                    # Update score breakdown
                    # ----------------------------------------

                    breakdown.ai_project_depth = ai_score
                    breakdown.python_backend = python_score
                    breakdown.cloud_fullstack = cloud_score
                    breakdown.github = github_score
                    breakdown.engineering_depth = (
                        engineering_score
                    )

                    # ----------------------------------------
                    # Recalculate total
                    # ----------------------------------------

                    total = (
                        ai_score
                        + python_score
                        + cloud_score
                        + github_score
                        + engineering_score
                    )

                    # ----------------------------------------
                    # Gemini strengths
                    # ----------------------------------------

                    llm_strengths = (
                        llm_result.get(
                            "strengths",
                            []
                        )
                    )

                    if isinstance(
                        llm_strengths,
                        list
                    ):

                        cleaned_strengths = [
                            str(item).strip()
                            for item in llm_strengths
                            if str(item).strip()
                        ]

                        if cleaned_strengths:
                            strengths = (
                                cleaned_strengths[:5]
                            )

                    # ----------------------------------------
                    # Gemini concerns
                    # ----------------------------------------

                    llm_concerns = (
                        llm_result.get(
                            "concerns",
                            []
                        )
                    )

                    if isinstance(
                        llm_concerns,
                        list
                    ):

                        cleaned_concerns = [
                            str(item).strip()
                            for item in llm_concerns
                            if str(item).strip()
                        ]

                        if cleaned_concerns:
                            concerns = (
                                cleaned_concerns[:5]
                            )

                    # ----------------------------------------
                    # Gemini evidence
                    # ----------------------------------------

                    llm_evidence = (
                        llm_result.get(
                            "evidence",
                            []
                        )
                    )

                    if isinstance(
                        llm_evidence,
                        list
                    ):

                        cleaned_evidence = [
                            str(item).strip()
                            for item in llm_evidence
                            if str(item).strip()
                        ]

                        if cleaned_evidence:
                            evidence = (
                                cleaned_evidence[:10]
                            )

                    # ----------------------------------------
                    # Mark successful Gemini analysis
                    # ----------------------------------------

                    analysis_method = "gemini"

                    print(
                        f"    → Gemini ✓ "
                        f"Score: {total}/100"
                    )

                except Exception as llm_error:

                    # IMPORTANT:
                    # Gemini failure must NOT fail resume.

                    analysis_method = (
                        "rule_based_fallback"
                    )

                    fallback_message = (
                        "LLM analysis unavailable; "
                        "rule-based scoring used"
                    )

                    if (
                        fallback_message
                        not in concerns
                    ):
                        concerns.append(
                            fallback_message
                        )

                    print(
                        f"    → Gemini ✗ "
                        f"Fallback used"
                    )

                    print(
                        f"       Reason: {llm_error}"
                    )

            else:

                fallback_message = (
                    "LLM analysis unavailable; "
                    "rule-based scoring used"
                )

                if fallback_message not in concerns:
                    concerns.append(
                        fallback_message
                    )

                print(
                    f"    → Rule-based scoring "
                    f"Score: {total}/100"
                )

            # ------------------------------------------------
            # 9. Final eligible candidate result
            # ------------------------------------------------

            results.append(
                CandidateResult(
                    candidate_name=candidate_name,
                    eligible=True,
                    matched_skills=candidate.skills,
                    total_score=total,
                    score_breakdown=breakdown,
                    project_summary=project_summary,
                    github_summary=gh.get(
                        "summary",
                        ""
                    ),
                    strengths=strengths,
                    concerns=concerns,
                    evidence=evidence,
                    analysis_method=analysis_method,
                    source_file=path.name,
                )
            )

            print(
                f"    → ELIGIBLE | "
                f"{candidate_name} | "
                f"{total}/100"
            )

            print()

        except Exception as error:

            # ------------------------------------------------
            # One broken resume must not stop the batch
            # ------------------------------------------------

            summary.failed_unreadable += 1

            print(
                f"    → FAILED: {error}"
            )

            print()

    # ========================================================
    # Sort results
    # ========================================================

    results.sort(
        key=lambda result: (
            result.eligible,
            result.total_score
        ),
        reverse=True
    )

    # ========================================================
    # Assign ranks
    # ========================================================

    rank = 1

    for result in results:

        if result.eligible:

            result.rank = rank

            rank += 1

    # ========================================================
    # Final output
    # ========================================================

    elapsed = (
        time.perf_counter()
        - start_time
    )

    print("==============================================")
    print("           SCREENING COMPLETED")
    print("==============================================")

    print(
        f"Total resumes : "
        f"{summary.total_resumes}"
    )

    print(
        f"Parsed        : "
        f"{summary.successfully_parsed}"
    )

    print(
        f"Eligible      : "
        f"{summary.eligible}"
    )

    print(
        f"Rejected      : "
        f"{summary.rejected}"
    )

    print(
        f"Failed        : "
        f"{summary.failed_unreadable}"
    )

    print(
        f"Time          : "
        f"{elapsed:.2f} seconds"
    )

    print("==============================================")

    return ScreeningOutput(
        batch_summary=summary,
        candidates=results
    )