import argparse
import json
from pathlib import Path

from dotenv import load_dotenv

from src.llm_analyzer import LLMAnalyzer
from src.pipeline import screen_directory


# Load variables from .env
load_dotenv()


def main():
    parser = argparse.ArgumentParser(
        description="AI Resume Screening & Ranking System"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Directory containing resume files"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Output JSON path"
    )

    args = parser.parse_args()

    # --------------------------------------------------
    # Initialize LLM analyzer
    # --------------------------------------------------

    try:
        llm_analyzer = LLMAnalyzer()
        print("LLM analyzer: enabled")

    except Exception as e:
        print(f"Warning: LLM unavailable: {e}")
        llm_analyzer = None

    # --------------------------------------------------
    # Run resume screening pipeline
    # --------------------------------------------------

    result = screen_directory(
        args.input,
        llm_analyzer=llm_analyzer
    )

    # --------------------------------------------------
    # Create output directory if needed
    # --------------------------------------------------

    output = Path(args.output)
    output.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------
    # Save results
    # --------------------------------------------------

    output.write_text(
        json.dumps(
            result.model_dump(),
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    # --------------------------------------------------
    # Print summary
    # --------------------------------------------------

    print()
    print("========== SCREENING SUMMARY ==========")
    print(
        f"Processed : "
        f"{result.batch_summary.total_resumes}"
    )
    print(
        f"Parsed    : "
        f"{result.batch_summary.successfully_parsed}"
    )
    print(
        f"Eligible  : "
        f"{result.batch_summary.eligible}"
    )
    print(
        f"Rejected  : "
        f"{result.batch_summary.rejected}"
    )
    print(
        f"Failed    : "
        f"{result.batch_summary.failed_unreadable}"
    )
    print(
        f"Results   : {output}"
    )
    print("=======================================")


if __name__ == "__main__":
    main()