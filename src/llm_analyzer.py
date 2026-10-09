import os
import json
from typing import Any, Dict

from google import genai
from pydantic import BaseModel, Field


class LLMAnalysis(BaseModel):
    candidate_name: str = ""
    project_summary: str = ""

    # Required 100-point scoring components
    ai_project_depth: int = Field(default=0, ge=0, le=40)
    python_backend: int = Field(default=0, ge=0, le=30)
    cloud_fullstack: int = Field(default=0, ge=0, le=15)
    engineering_depth: int = Field(default=0, ge=0, le=5)

    strengths: list[str] = Field(default_factory=list)
    concerns: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)


class LLMAnalyzer:

    def __init__(self):
        # --------------------------------------------------
        # Load Gemini API key
        # --------------------------------------------------

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not set"
            )

        # --------------------------------------------------
        # Initialize Gemini client
        # --------------------------------------------------

        self.client = genai.Client(
            api_key=api_key
        )

        # --------------------------------------------------
        # Gemini model
        # --------------------------------------------------

        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.1-flash-lite"
        )

    def analyze(
        self,
        resume_text: str
    ) -> Dict[str, Any]:

        # --------------------------------------------------
        # Validate input
        # --------------------------------------------------

        if not resume_text or not resume_text.strip():
            raise ValueError(
                "Resume text is empty"
            )

        # --------------------------------------------------
        # Prompt
        # --------------------------------------------------

        prompt = f"""
You are an AI resume screening evaluator for an SDE Intern role.

Analyze ONLY the resume provided below.

IMPORTANT RULES:

1. Do NOT invent experience.
2. Use ONLY evidence explicitly present in the resume.
3. Do not give high scores merely because a framework name appears
   in the skills section.
4. Give higher scores when the candidate explains what they built,
   how it works, technologies used, backend logic, data flow,
   retrieval, evaluation, deployment, testing, or architecture.
5. Prefer evidence from projects, internships and work experience
   over a simple skills list.
6. A simple "used OpenAI API" or "used Gemini API" project should
   receive a low AI score.
7. A genuine RAG system involving document processing,
   chunking, embeddings, vector search and retrieval should receive
   a significantly higher AI score.
8. Agentic systems involving tools, state, orchestration,
   multi-agent workflows or evaluation should receive higher scores.
9. Do not assume technologies that are not explicitly mentioned.
10. Be conservative when evidence is weak.

--------------------------------------------------
SCORING
--------------------------------------------------

AI / Agentic / RAG Project Depth: 0-40

0-10:
Only LLM/API exposure, simple chatbot, or thin wrapper.

11-20:
Actual AI project using an LLM but limited workflow or engineering
depth.

21-30:
RAG, embeddings, vector search, document processing, retrieval,
or meaningful AI backend implementation.

31-35:
Strong RAG or agentic workflow involving retrieval, tools,
state, orchestration, backend logic, evaluation, or substantial
product logic.

36-40:
Multiple strong AI systems OR an advanced agentic/RAG system with
substantial engineering depth, evaluation, and production-like
implementation.

--------------------------------------------------

Python & Backend Engineering: 0-30

Reward:

- Genuine Python implementation
- FastAPI
- Django
- Flask
- REST APIs
- backend services
- async programming
- databases
- authentication
- background processing
- production-like backend architecture

Do NOT give a high score just because Python appears in a skills
section.

--------------------------------------------------

Cloud / Deployment / Full Stack: 0-15

Reward:

- AWS
- Azure
- GCP
- Docker
- deployment
- CI/CD
- React
- Next.js
- end-to-end applications
- frontend + backend integration

--------------------------------------------------

Engineering Depth: 0-5

Reward evidence of:

- testing
- architecture
- caching
- queues
- concurrency
- error handling
- observability
- scalability
- performance optimization
- security

--------------------------------------------------

CANDIDATE NAME

Extract the actual candidate's name from the resume.

Do NOT use:

- LinkedIn
- GitHub
- Email
- Skills
- Projects
- Resume
- Job titles
- Section headings

If the name cannot be determined, return:

"Unknown"

--------------------------------------------------

PROJECT SUMMARY

Write a concise summary of the strongest relevant project(s).

Mention actual implementation details from the resume.

Bad:
"AI-related implementation detected."

Good:
"Built a document Q&A system using RAG with PDF processing,
embeddings, vector search and an LLM-backed conversational layer."

Do not invent missing details.

--------------------------------------------------

STRENGTHS

Return 2-5 concise evidence-based strengths.

Example:

[
  "Built a RAG pipeline using embeddings and vector search",
  "Developed Python backend APIs using FastAPI",
  "Deployed the application using Docker"
]

--------------------------------------------------

CONCERNS

Return 0-4 evidence-based concerns.

Examples:

[
  "AI experience is primarily limited to API integration",
  "Limited evidence of testing",
  "No clear production deployment experience"
]

Do not create concerns when there is no evidence for them.

--------------------------------------------------

EVIDENCE

Return 3-8 short pieces of evidence from the resume supporting
the evaluation.

Do not quote long passages.

--------------------------------------------------

OUTPUT

Return ONLY valid JSON.

The JSON must exactly follow this structure:

{{
    "candidate_name": "string",
    "project_summary": "string",
    "ai_project_depth": 0,
    "python_backend": 0,
    "cloud_fullstack": 0,
    "engineering_depth": 0,
    "strengths": [],
    "concerns": [],
    "evidence": []
}}

--------------------------------------------------
RESUME
--------------------------------------------------

---BEGIN RESUME---

{resume_text}

---END RESUME---
"""

        # --------------------------------------------------
        # Gemini request
        #
        # IMPORTANT:
        # The Google GenAI SDK already performs retry handling.
        # We intentionally do NOT add another retry loop here.
        # --------------------------------------------------

        try:

            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={
                    "response_mime_type": "application/json"
                }
            )

        except Exception as exc:

            error_text = str(exc)

            # Convert temporary Gemini failures into a clear
            # exception. The pipeline can catch this and continue
            # processing the remaining resumes.

            if (
                "503" in error_text
                or "UNAVAILABLE" in error_text
                or "429" in error_text
                or "RESOURCE_EXHAUSTED" in error_text
                or "500" in error_text
                or "502" in error_text
                or "504" in error_text
            ):
                raise RuntimeError(
                    f"Temporary Gemini service error: {exc}"
                ) from exc

            raise

        # --------------------------------------------------
        # Validate response
        # --------------------------------------------------

        if response is None:
            raise ValueError(
                "Gemini returned no response"
            )

        response_text = getattr(
            response,
            "text",
            None
        )

        if not response_text:
            raise ValueError(
                "Gemini returned empty response"
            )

        # --------------------------------------------------
        # Parse JSON
        # --------------------------------------------------

        try:

            data = json.loads(
                response_text
            )

        except json.JSONDecodeError as exc:

            raise ValueError(
                "Gemini returned invalid JSON"
            ) from exc

        # --------------------------------------------------
        # Ensure JSON object
        # --------------------------------------------------

        if not isinstance(data, dict):

            raise ValueError(
                "Gemini response is not a JSON object"
            )

        # --------------------------------------------------
        # Validate using Pydantic
        # --------------------------------------------------

        try:

            result = LLMAnalysis.model_validate(
                data
            )

        except Exception as exc:

            raise ValueError(
                f"Gemini response failed schema validation: {exc}"
            ) from exc

        # --------------------------------------------------
        # Return validated dictionary
        # --------------------------------------------------

        return result.model_dump()