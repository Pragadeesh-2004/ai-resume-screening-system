import re
from datetime import datetime, timezone
from typing import Dict, Optional

import requests


# ---------------------------------------------------------
# GitHub URL pattern
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


def username_from_url(url: Optional[str]) -> Optional[str]:
    if not url:
        return None

    match = GITHUB_RE.search(url.strip())

    if not match:
        return None

    username = match.group(1)

    reserved = {
        "features", "topics", "collections", "events",
        "explore", "login", "signup", "settings", "about",
        "pricing", "enterprise", "marketplace", "orgs",
    }

    if username.lower() in reserved:
        return None

    return username
# ---------------------------------------------------------
# Check whether repository is Python / AI relevant
# ---------------------------------------------------------
def is_relevant_repo(repo: dict) -> bool:

    language = (
        repo.get("language") or ""
    ).lower()

    name = (
        repo.get("name") or ""
    ).lower()

    description = (
        repo.get("description") or ""
    ).lower()

    topics = " ".join(
        repo.get("topics") or []
    ).lower()

    text = f"{name} {description} {topics}"

    ai_terms = [
        "ai",
        "ml",
        "machine-learning",
        "machine learning",
        "llm",
        "rag",
        "agent",
        "genai",
        "generative-ai",
        "deep-learning",
        "deep learning",
        "vector",
        "langchain",
        "langgraph",
        "llamaindex",
        "tensorflow",
        "pytorch",
    ]

    python_relevant = language in {
        "python",
        "jupyter notebook",
    }

    ai_relevant = any(
        term in text
        for term in ai_terms
    )

    return python_relevant or ai_relevant


# ---------------------------------------------------------
# GitHub enrichment
# ---------------------------------------------------------
def enrich_github(
    url: Optional[str],
    token: Optional[str] = None,
) -> Dict:

    username = username_from_url(url)

    # -----------------------------------------------------
    # No GitHub profile
    # -----------------------------------------------------
    if not username:
        return {
            "score": 0,
            "summary": "No GitHub profile found.",
            "status": "missing",
        }

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "AI-Resume-Screening-System",
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    base_url = "https://api.github.com"

    try:

        # -------------------------------------------------
        # Get user information
        # -------------------------------------------------
        user_response = requests.get(
            f"{base_url}/users/{username}",
            headers=headers,
            timeout=8,
        )

        user_response.raise_for_status()

        user_data = user_response.json()

        # -------------------------------------------------
        # Get repositories
        # -------------------------------------------------
        repos_response = requests.get(
            f"{base_url}/users/{username}/repos",
            headers=headers,
            params={
                "per_page": 100,
                "sort": "updated",
            },
            timeout=8,
        )

        repos_response.raise_for_status()

        repos = repos_response.json()

        if not isinstance(repos, list):
            raise ValueError(
                "Invalid GitHub repository response"
            )

        # -------------------------------------------------
        # Calculate activity
        # -------------------------------------------------
        now = datetime.now(timezone.utc)

        recent_repos = 0
        relevant_repos = 0

        for repo in repos:

            # ---------------------------------------------
            # Recently updated repositories
            # ---------------------------------------------
            pushed_at = repo.get("pushed_at")

            if pushed_at:

                try:

                    updated_time = datetime.fromisoformat(
                        pushed_at.replace(
                            "Z",
                            "+00:00",
                        )
                    )

                    days_old = (
                        now - updated_time
                    ).days

                    if 0 <= days_old <= 180:
                        recent_repos += 1

                except (ValueError, TypeError):
                    pass

            # ---------------------------------------------
            # Python / AI relevant repositories
            # ---------------------------------------------
            if is_relevant_repo(repo):
                relevant_repos += 1

        # -------------------------------------------------
        # Assignment scoring
        #
        # Recent activity : 0-5
        # Relevant repos  : 0-5
        # Total           : 0-10
        # -------------------------------------------------
        recent_points = min(
            5,
            recent_repos,
        )

        relevant_points = min(
            5,
            relevant_repos,
        )

        score = (
            recent_points
            + relevant_points
        )

        # -------------------------------------------------
        # Summary
        # -------------------------------------------------
        public_repos = int(
            user_data.get(
                "public_repos",
                0,
            )
        )

        summary = (
            f"{public_repos} public repositories; "
            f"{recent_repos} recently updated; "
            f"{relevant_repos} Python/AI-relevant repositories."
        )

        return {
            "score": score,
            "summary": summary,
            "status": "success",
        }

    # -----------------------------------------------------
    # GitHub failure must NOT fail resume screening
    # -----------------------------------------------------
    except requests.RequestException as exc:

        return {
            "score": 0,
            "summary": (
                "GitHub enrichment unavailable: "
                f"{type(exc).__name__}"
            ),
            "status": "error",
        }

    except (
        ValueError,
        TypeError,
        KeyError,
    ) as exc:

        return {
            "score": 0,
            "summary": (
                "GitHub enrichment unavailable: "
                f"{type(exc).__name__}"
            ),
            "status": "error",
        }

    except Exception as exc:

        return {
            "score": 0,
            "summary": (
                "GitHub enrichment unavailable: "
                f"{type(exc).__name__}"
            ),
            "status": "error",
        }