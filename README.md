Absolutely. Here is a **clean, professional README.md** you can directly use for your assignment. I’ve kept it clear and aligned with the actual project scope, without claiming features that are not implemented.

```markdown
# AI Resume Screening & Ranking System

A Python-based CLI application that automatically screens resumes for an SDE internship role, filters candidates based on Python and AI/LLM/agentic experience, ranks eligible candidates using a 100-point scoring model, optionally enriches GitHub activity, and generates structured JSON results.

---

## Features

- 📄 PDF resume ingestion using PyMuPDF
- 🔎 Candidate information extraction
  - Name
  - Email
  - Skills
  - GitHub profile
  - AI/LLM-related evidence
- ✅ Hard eligibility filtering
  - Python experience is required
  - Meaningful AI/LLM/RAG/agentic evidence is required
- 📊 Explainable 100-point candidate scoring
- 🐙 Optional GitHub activity enrichment
- 🛡️ Graceful handling of malformed resumes
- ⚠️ GitHub/API failures do not stop the screening process
- 🧠 Optional LLM-based semantic analysis
- 📦 Machine-readable JSON output
- 🧪 Automated tests with pytest

---

## Project Architecture

```text
AI-Resume-Screening/
│
├── src/
│   ├── __init__.py
│   ├── eligibility.py
│   ├── extractor.py
│   ├── github.py
│   ├── llm.py
│   ├── llm_analyzer.py
│   ├── models.py
│   ├── parser.py
│   ├── pipeline.py
│   └── scorer.py
│
├── tests/
│
├── resumes/
│   └── *.pdf
│
├── output/
│   └── results.json
│
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## How the System Works

The screening pipeline follows these steps:

```text
Resume Folder
      │
      ▼
Resume Ingestion
      │
      ▼
Text Extraction
      │
      ▼
Candidate Information Extraction
      │
      ▼
Hard Eligibility Filtering
      │
      ├── Not Eligible ──► Rejection Reason
      │
      ▼
Eligible Candidates
      │
      ▼
Candidate Scoring
      │
      ▼
GitHub Enrichment
      │
      ▼
Optional LLM Analysis
      │
      ▼
Ranking
      │
      ▼
results.json
```

---

# Setup

## 1. Clone the Repository

```bash
git clone <your-repository-url>
cd AI-Resume-Screening
```

---

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Create a `.env` file from `.env.example`.

```bash
cp .env.example .env
```

On Windows, you can also create `.env` manually.

Example:

```env
GEMINI_API_KEY=
GEMINI_MODEL=gemini-3.1-flash-lite
GITHUB_TOKEN=
```

### Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | No | Enables optional Gemini-based analysis |
| `GEMINI_MODEL` | No | Gemini model name |
| `GITHUB_TOKEN` | No | Optional GitHub API authentication |

The application can run without these credentials using deterministic rule-based screening.

**Never commit `.env` or API keys to Git.**

---

# Running the Application

Place resumes inside the `resumes/` directory.

Example:

```text
resumes/
├── candidate_01.pdf
├── candidate_02.pdf
├── candidate_03.pdf
└── ...
```

Run:

```bash
python main.py --input ./resumes --output ./output/results.json
```

Example console output:

```text
========== SCREENING SUMMARY ==========
Processed : 50
Parsed    : 50
Eligible  : 39
Rejected  : 11
Failed    : 0
Results   : output/results.json
=======================================
```

---

# Resume Processing

The application extracts text from each resume and identifies relevant candidate information.

The extracted information can include:

- Candidate name
- Email address
- Technical skills
- AI/LLM technologies
- Project evidence
- GitHub profile

The system is designed to continue processing other resumes if an individual resume cannot be parsed.

---

# Eligibility Filtering

Eligibility is treated as a **hard filter** before ranking.

A candidate must demonstrate both:

### 1. Python Evidence

Examples include:

```text
Python
Python 3
FastAPI
Django
Flask
Pandas
NumPy
PyTorch
TensorFlow
Scikit-learn
```

### 2. Meaningful AI / Agentic Evidence

Examples include:

```text
RAG
Retrieval-Augmented Generation
LangChain
LangGraph
LlamaIndex
Embeddings
Vector Search
Vector Database
AI Agents
Agentic AI
Multi-Agent Systems
Tool Calling
Function Calling
Semantic Search
```

Candidates who do not satisfy both requirements are rejected before ranking.

The rejection reason is included in the output.

---

# Scoring Model

Eligible candidates are scored out of **100 points**.

| Category | Maximum Score |
|---|---:|
| AI / Agentic / RAG Project Depth | 40 |
| Python & Backend Engineering | 30 |
| Cloud / Full Stack | 15 |
| GitHub Activity | 10 |
| Engineering Depth | 5 |
| **Total** | **100** |

---

## 1. AI / Agentic / RAG Project Depth — 40 Points

This is the most heavily weighted category.

The system looks for evidence such as:

- RAG pipelines
- Embeddings
- Vector search
- Document ingestion
- Chunking
- Semantic search
- Agentic workflows
- Tool/function calling
- Multi-agent workflows
- LLM orchestration
- Evaluation
- Reranking
- AI backend integration

A simple API wrapper around an LLM receives less credit than a project demonstrating an actual AI workflow.

---

## 2. Python & Backend Engineering — 30 Points

Signals include:

- Python
- FastAPI
- Flask
- Django
- REST APIs
- Backend development
- Async programming
- PostgreSQL
- Redis
- API development

---

## 3. Cloud / Full Stack — 15 Points

Signals include technologies and experience such as:

- AWS
- Azure
- GCP
- Docker
- React
- Next.js
- Deployment
- Vercel
- Render

---

## 4. GitHub Activity — 10 Points

When a public GitHub profile is available, the system checks:

- Public repositories
- Recently updated repositories
- Python-related repositories
- AI/ML-related repositories

GitHub enrichment is treated as an additional ranking signal.

A missing or unavailable GitHub profile does **not** make a candidate ineligible.

---

## 5. Engineering Depth — 5 Points

Additional engineering signals include:

- Testing
- Pytest
- Error handling
- Exception handling
- Caching
- Concurrency
- Logging
- Architecture
- Modular architecture
- Microservices
- Modular monolith

---

# LLM Integration

The project supports optional LLM-based analysis for semantic understanding of resume content.

The LLM layer is isolated from the core screening pipeline.

This means:

```text
Core Screening
      │
      ├── Rule-based eligibility
      ├── Deterministic scoring
      └── GitHub enrichment
           
Optional
      │
      ▼
LLM Semantic Analysis
```

The core pipeline does not depend entirely on an LLM.

If the LLM is unavailable or an API request fails, the application can continue using the rule-based fallback mechanism.

This prevents a single API failure from stopping the complete batch.

---

# Fallback Mechanism

Reliability is an important part of the system.

The application handles failures at the individual resume level instead of terminating the entire batch.

Examples:

### Malformed Resume

```text
Resume 1 → Success
Resume 2 → Parsing failed
Resume 3 → Success
Resume 4 → Success
```

Resume 2 is recorded as failed while the remaining resumes continue processing.

### GitHub Failure

If GitHub enrichment fails:

```text
GitHub unavailable
        ↓
Score = 0
        ↓
Continue screening
```

The candidate is **not rejected** because of GitHub failure.

### LLM Failure

If LLM analysis fails:

```text
LLM analysis
     ↓
   Failed
     ↓
Rule-based fallback
     ↓
Continue ranking
```

---

# Output Format

The application generates a JSON file containing:

- Batch summary
- Candidate ranking
- Eligibility status
- Rejection reasons
- Total score
- Score breakdown
- Matched skills
- Project summary
- GitHub summary
- Strengths
- Concerns
- Evidence
- Source resume

Example:

```json
{
  "batch_summary": {
    "total_resumes": 50,
    "successfully_parsed": 50,
    "eligible": 39,
    "rejected": 11,
    "failed_unreadable": 0
  },
  "candidates": [
    {
      "rank": 1,
      "candidate_name": "Candidate Name",
      "eligible": true,
      "total_score": 82,
      "score_breakdown": {
        "ai_project_depth": 34,
        "python_backend": 25,
        "cloud_fullstack": 10,
        "github": 8,
        "engineering_depth": 5
      },
      "matched_skills": [
        "Python",
        "FastAPI",
        "RAG",
        "LangChain"
      ],
      "project_summary": "...",
      "github_summary": "...",
      "strengths": [],
      "concerns": [],
      "evidence": []
    }
  ]
}
```

---

# Testing

Run the test suite using:

```bash
pytest -q
```

The tests cover important screening behavior such as:

- Python eligibility
- AI/agentic eligibility
- Candidate scoring
- Edge cases
- Failure handling

---

# Handling Different Resume Formats

The project can be extended to support additional resume formats.

Current parser support:

```text
PDF
DOCX
TXT
```

PDF resumes are processed using **PyMuPDF**.

DOCX support uses **python-docx**.

TXT files are read directly as text.

---

# Design Decisions

## 1. Hard Filtering Before Ranking

Eligibility is intentionally handled outside the LLM.

A candidate must demonstrate both:

```text
Python
   AND
Meaningful AI / Agentic Experience
```

This prevents an otherwise strong software profile without relevant AI experience from receiving a high ranking.

---

## 2. Explainable Scoring

The scoring system is deterministic and based on explicit evidence.

Instead of returning only:

```text
Score = 82
```

the system provides:

```text
AI Project Depth       = 34
Python & Backend       = 25
Cloud / Full Stack     = 10
GitHub                 = 8
Engineering Depth      = 5
--------------------------------
Total                  = 82
```

This makes the ranking easier to understand and audit.

---

## 3. AI Project Quality Matters

The system does not treat every mention of AI equally.

For example:

```text
"Built a chatbot using OpenAI API"
```

is weaker evidence than:

```text
"Built a RAG pipeline with document ingestion,
chunking, embeddings, vector search and LLM generation."
```

Implementation depth is therefore used as an important ranking signal.

---

## 4. GitHub Is an Additional Signal

GitHub activity is not used as a hard eligibility requirement.

This avoids unfairly rejecting candidates who:

- Do not provide GitHub
- Have private repositories
- Have an unavailable profile
- Encounter GitHub API/rate-limit issues

---

## 5. Failure Isolation

Failures are isolated at the smallest practical level.

A single:

- malformed resume
- GitHub API failure
- LLM failure
- unexpected parsing error

should not terminate the entire screening batch.

---

# Repository Structure

```text
.
├── src/
│   ├── eligibility.py       # Hard eligibility rules
│   ├── extractor.py         # Candidate field extraction
│   ├── github.py            # GitHub enrichment
│   ├── llm.py               # LLM adapter
│   ├── llm_analyzer.py      # LLM-based analysis
│   ├── models.py            # Pydantic data models
│   ├── parser.py            # Resume text extraction
│   ├── pipeline.py          # Main screening pipeline
│   └── scorer.py            # Deterministic scoring
│
├── tests/                   # Automated tests
├── resumes/                 # Input resumes
├── output/                  # Generated results
│
├── main.py                  # CLI entry point
├── requirements.txt         # Python dependencies
├── .env.example             # Environment configuration example
├── .gitignore
└── README.md
```

---

# Example Workflow

```bash
# 1. Create environment
python -m venv .venv

# 2. Activate environment
.venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
# Create .env and add optional API keys

# 5. Run screening
python main.py --input ./resumes --output ./output/results.json

# 6. Run tests
pytest -q
```

---

# Limitations

The current implementation has some limitations:

- Scanned/image-only PDFs may not contain extractable text.
- GitHub enrichment depends on public GitHub API availability.
- LLM analysis depends on the configured provider and API availability.
- Resume quality and formatting can affect text extraction.
- Rule-based scoring is based on observable resume evidence and may not capture every nuance of a candidate's experience.

---

# If I Had More Time

1. **Structured LLM extraction**
   - Use Pydantic structured output for deeper project and experience analysis.
   - Return evidence snippets for every important score.

2. **OCR fallback**
   - Add OCR support for scanned/image-only resumes.

3. **Async processing and caching**
   - Add bounded asynchronous GitHub/LLM calls.
   - Cache repeated GitHub lookups and LLM analysis.

4. **Stronger test dataset**
   - Add integration tests using a synthetic resume dataset covering:
     - Strong AI candidates
     - Strong Python but weak AI candidates
     - AI candidates without Python
     - Malformed resumes
     - Missing GitHub profiles

---

# Technologies Used

- **Python**
- **PyMuPDF**
- **Pydantic**
- **Requests**
- **python-dotenv**
- **pytest**
- **Google Gemini API** — optional
- **GitHub REST API** — optional

---

# License

This project was developed as part of an SDE Intern coding assignment.
```

### One important change from your current README

Your current README says:

> "Read every PDF in the input directory."

But your implementation has been extended to support **PDF, DOCX, and TXT**, so the README should say:

> **Read supported resume files (PDF, DOCX, and TXT) from the input directory.**

Also, don't say **“LLM adapter can be added”** if your project already contains `llm.py` and `llm_analyzer.py`. The README above correctly describes it as **optional LLM integration**.