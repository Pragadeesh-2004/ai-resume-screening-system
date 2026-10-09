from typing import List, Optional

from pydantic import BaseModel, Field


class Project(BaseModel):
    name: str = ""
    description: str = ""
    technologies: List[str] = Field(
        default_factory=list
    )
    ai_depth: str = "unknown"
    evidence: List[str] = Field(
        default_factory=list
    )


class Candidate(BaseModel):
    name: str = "Unknown"
    email: Optional[str] = None
    skills: List[str] = Field(
        default_factory=list
    )
    projects: List[Project] = Field(
        default_factory=list
    )
    github_url: Optional[str] = None
    raw_text: str = ""


class ScoreBreakdown(BaseModel):
    """
    Assignment scoring:

    AI / Agentic / RAG      = 40
    Python / Backend        = 30
    Cloud / Full Stack      = 15
    GitHub                  = 10
    Engineering Depth       = 5

    Total                   = 100
    """

    ai_project_depth: int = Field(
        default=0,
        ge=0,
        le=40
    )

    python_backend: int = Field(
        default=0,
        ge=0,
        le=30
    )

    cloud_fullstack: int = Field(
        default=0,
        ge=0,
        le=15
    )

    github: int = Field(
        default=0,
        ge=0,
        le=10
    )

    engineering_depth: int = Field(
        default=0,
        ge=0,
        le=5
    )


class CandidateResult(BaseModel):
    """
    Final screening result for one candidate.
    """

    # --------------------------------------------------
    # Ranking
    # --------------------------------------------------

    rank: Optional[int] = None

    # --------------------------------------------------
    # Candidate information
    # --------------------------------------------------

    candidate_name: str

    eligible: bool

    # --------------------------------------------------
    # Eligibility
    # --------------------------------------------------

    rejection_reasons: List[str] = Field(
        default_factory=list
    )

    matched_skills: List[str] = Field(
        default_factory=list
    )

    # --------------------------------------------------
    # Scoring
    # --------------------------------------------------

    total_score: int = Field(
        default=0,
        ge=0,
        le=100
    )

    score_breakdown: ScoreBreakdown = Field(
        default_factory=ScoreBreakdown
    )

    # --------------------------------------------------
    # Candidate analysis
    # --------------------------------------------------

    project_summary: str = ""

    github_summary: str = ""

    strengths: List[str] = Field(
        default_factory=list
    )

    concerns: List[str] = Field(
        default_factory=list
    )

    # --------------------------------------------------
    # Evidence
    #
    # Evidence explains why the candidate received
    # the given evaluation.
    # --------------------------------------------------

    evidence: List[str] = Field(
        default_factory=list
    )

    # --------------------------------------------------
    # Analysis method
    #
    # "gemini"                  -> Gemini analysis succeeded
    # "rule_based_fallback"     -> Gemini failed/unavailable
    # --------------------------------------------------

    analysis_method: str = "rule_based_fallback"

    # --------------------------------------------------
    # Source resume
    # --------------------------------------------------

    source_file: str = ""


class BatchSummary(BaseModel):
    """
    Overall batch processing statistics.
    """

    total_resumes: int = 0

    successfully_parsed: int = 0

    eligible: int = 0

    rejected: int = 0

    failed_unreadable: int = 0


class ScreeningOutput(BaseModel):
    """
    Complete screening output.
    """

    batch_summary: BatchSummary

    candidates: List[CandidateResult]