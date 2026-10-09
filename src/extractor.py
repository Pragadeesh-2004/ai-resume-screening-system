import re
from typing import List, Optional

from .models import Candidate, Project


# ---------------------------------------------------------
# Email
# ---------------------------------------------------------
EMAIL_RE = re.compile(
    r"\b[A-Za-z0-9._%+-]+"
    r"@[A-Za-z0-9.-]+\."
    r"[A-Za-z]{2,}\b"
)


# ---------------------------------------------------------
# GitHub URL
#
# Supports:
# https://github.com/username
# http://github.com/username
# www.github.com/username
# github.com/username
# ---------------------------------------------------------
GITHUB_RE = re.compile(
    r"(?:https?://)?(?:www\.)?github\.com/"
    r"([A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?)"
    r"(?=[/?#\s]|$)",
    re.IGNORECASE,
)


# ---------------------------------------------------------
# GitHub reserved paths
# ---------------------------------------------------------
GITHUB_RESERVED = {
    "features",
    "topics",
    "collections",
    "events",
    "explore",
    "login",
    "signup",
    "settings",
    "about",
    "pricing",
    "enterprise",
    "marketplace",
    "orgs",
}


# ---------------------------------------------------------
# Skills
# ---------------------------------------------------------
KNOWN_SKILLS = [
    "python",
    "python3",
    "fastapi",
    "django",
    "flask",
    "asyncio",
    "postgresql",
    "postgres",
    "redis",
    "docker",
    "gcp",
    "aws",
    "azure",
    "react",
    "next.js",
    "nextjs",
    "javascript",
    "typescript",
    "node.js",
    "nodejs",
    "java",
    "c++",
    "sql",
    "langchain",
    "langgraph",
    "llamaindex",
    "google adk",
    "rag",
    "embeddings",
    "vector search",
    "vector database",
    "vector db",
    "openai",
    "gemini",
    "llm",
    "agents",
    "agentic ai",
    "tensorflow",
    "pytorch",
    "scikit-learn",
    "mongodb",
    "git",
]


# ---------------------------------------------------------
# AI-related terms
# ---------------------------------------------------------
AI_TERMS = [
    "langchain",
    "langgraph",
    "llamaindex",
    "google adk",
    "rag",
    "retrieval augmented generation",
    "retrieval-augmented generation",
    "embeddings",
    "vector search",
    "vector database",
    "vector db",
    "llm",
    "large language model",
    "tool calling",
    "function calling",
    "ai agent",
    "agentic",
    "agentic ai",
    "multi-agent",
    "multi agent",
]


# ---------------------------------------------------------
# Name filtering
# ---------------------------------------------------------
INVALID_NAME_TERMS = {
    "linkedin",
    "github",
    "email",
    "phone",
    "mobile",
    "resume",
    "curriculum vitae",
    "skills",
    "technical skills",
    "experience",
    "work experience",
    "education",
    "projects",
    "project",
    "certifications",
    "profile",
    "objective",
    "summary",
    "software engineer",
    "software engineering",
    "job simulation",
    "contribute to",
}


# ---------------------------------------------------------
# Check whether a line looks like a name
# ---------------------------------------------------------
def _looks_like_name(line: str) -> bool:
    """
    Check whether a line is likely to be a candidate name.
    """

    line = line.strip()

    if not line:
        return False

    # Reasonable name length
    if len(line) < 3 or len(line) > 80:
        return False

    lower = line.lower()

    # Reject URLs
    if "http://" in lower or "https://" in lower:
        return False

    # Reject email
    if "@" in line:
        return False

    # Reject GitHub / LinkedIn lines
    if GITHUB_RE.search(line):
        return False

    if "linkedin" in lower:
        return False

    # Reject known section/header text
    for term in INVALID_NAME_TERMS:
        if term in lower:
            return False

    # Names generally should not contain digits
    if any(ch.isdigit() for ch in line):
        return False

    # Avoid lines with too many symbols
    letters = sum(
        ch.isalpha()
        for ch in line
    )

    if letters < 3:
        return False

    # Candidate name normally has 1–5 words
    words = line.split()

    if not 1 <= len(words) <= 5:
        return False

    # Reject lines dominated by separators
    if line.count("|") >= 2:
        return False

    if line.count(":") >= 2:
        return False

    return True


# ---------------------------------------------------------
# Candidate name extraction
# ---------------------------------------------------------
def _find_name(text: str) -> str:
    """
    Extract likely candidate name from the beginning
    of the resume.
    """

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    # -----------------------------------------------------
    # First look for explicit "Name:"
    # -----------------------------------------------------
    for line in lines[:20]:

        lower = line.lower()

        if lower.startswith("name:"):

            name = line.split(
                ":",
                1,
            )[1].strip()

            if _looks_like_name(name):
                return name[:80]

    # -----------------------------------------------------
    # Otherwise inspect first few lines
    # -----------------------------------------------------
    for line in lines[:15]:

        if _looks_like_name(line):
            return line[:80]

    return "Unknown"


# ---------------------------------------------------------
# GitHub extraction
# ---------------------------------------------------------
def _find_github(text: str) -> Optional[str]:
    """
    Find a GitHub profile URL in resume text.

    Returns a normalized URL:
        https://github.com/username
    """

    for match in GITHUB_RE.finditer(text):

        username = match.group(1)

        if username.lower() in GITHUB_RESERVED:
            continue

        return f"https://github.com/{username}"

    return None


# ---------------------------------------------------------
# Skill extraction
# ---------------------------------------------------------
def _skills(text: str) -> List[str]:
    lower = text.lower()

    found = []

    for skill in KNOWN_SKILLS:

        if skill in lower:
            found.append(skill)

    return sorted(set(found))


# ---------------------------------------------------------
# Project fallback extraction
# ---------------------------------------------------------
def _projects(text: str) -> List[Project]:
    """
    Lightweight fallback project extraction.

    The LLM will later provide richer project analysis.
    """

    lower = text.lower()

    ai_hits = [
        term
        for term in AI_TERMS
        if term in lower
    ]

    if not ai_hits:
        return []

    evidence = [
        f"Resume mentions {term}"
        for term in ai_hits[:8]
    ]

    return [
        Project(
            name="AI/LLM project evidence",
            description=(
                "AI-related implementation evidence "
                "detected in resume text."
            ),
            technologies=ai_hits[:10],
            ai_depth="medium",
            evidence=evidence,
        )
    ]


# ---------------------------------------------------------
# Main candidate extraction
# ---------------------------------------------------------
def extract_candidate(text: str) -> Candidate:

    email_match = EMAIL_RE.search(text)

    github_url = _find_github(text)

    return Candidate(
        name=_find_name(text),

        email=(
            email_match.group(0)
            if email_match
            else None
        ),

        skills=_skills(text),

        projects=_projects(text),

        github_url=github_url,

        raw_text=text,
    )