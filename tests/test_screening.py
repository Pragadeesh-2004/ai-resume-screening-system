from src.models import Candidate
from src.eligibility import check_eligibility
from src.scorer import score_candidate


def test_python_and_ai_is_eligible():
    c = Candidate(raw_text="Python FastAPI LangChain RAG embeddings")
    eligible, reasons = check_eligibility(c)
    assert eligible is True
    assert reasons == []


def test_missing_python_is_rejected():
    c = Candidate(raw_text="Java React LangChain RAG")
    eligible, reasons = check_eligibility(c)
    assert eligible is False
    assert "No evidence of Python stack" in reasons


def test_missing_ai_is_rejected():
    c = Candidate(raw_text="Python FastAPI PostgreSQL")
    eligible, reasons = check_eligibility(c)
    assert eligible is False
    assert "No AI/agentic project evidence" in reasons


def test_score_is_at_most_100():
    c = Candidate(raw_text=("Python FastAPI Redis PostgreSQL Docker GCP React "
                            "RAG LangChain LangGraph embeddings vector search agent "
                            "testing pytest caching queue observability concurrency architecture"))
    breakdown, total = score_candidate(c, github_score=10)
    assert total <= 100
    assert breakdown.github == 10
