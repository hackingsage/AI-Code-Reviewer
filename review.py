import argparse
import json
from typing import List
from core.parser import parse_file
from core.types import Issue, ReviewResult
from analyzers import (
    complexity,
    patterns,
    security,
    unused,
    performance,
    logic,
    style,
)
from llm.client import LLMClient
from llm.ollama_client import ollama_call

def run_analyzers(parsed) -> List[Issue]:
    issues: List[Issue] = []

    for fn in parsed["functions"]:
        issues.extend(complexity.analyze(fn))
        issues.extend(patterns.analyze(fn))
        issues.extend(security.analyze(fn))
        issues.extend(unused.analyze(fn))
        issues.extend(performance.analyze(fn))
        issues.extend(logic.analyze(fn))
        issues.extend(style.analyze(fn))

    return issues

def main():
    parser = argparse.ArgumentParser(description="AI-powered code review")
    parser.add_argument("file", help="Path to Python file to review")
    parser.add_argument(
        '--json',
        action="store_true",
        help="Emit JSON output"
    )
    # parser.add_argument(
    #     "--no-ai",
    #     action="store_true",
    #     help="Disable AI explanations",
    # )

    args = parser.parse_args()

    parsed = parse_file(args.file)
    issues = run_analyzers(parsed)

    results: List[dict] = []

    llm = LLMClient(
        model_call=lambda prompt, system: ollama_call(
            prompt, system, model="deepseek-coder:6.7b"
        )
    )

    for issue in issues:
        entry = issue.to_dict()
        results.append(entry)

    for entry, issue in zip(results, issues):
        ai_review = llm.review_issue(issue)
        fix = llm.generate_fix(issue)

        if ai_review:
            entry["ai"] = ai_review.to_dict()
        if fix:
            entry["fix"] = fix

    if args.json:
        with open("review.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
    else:
        for r in results:
            print(f"[{r['category']}] Line {r['line']}: {r['message']}")
    


if __name__ == "__main__":
    main()