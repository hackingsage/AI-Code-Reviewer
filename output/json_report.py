import json
from typing import List
from core.types import ReviewResult

def write_json(results: List[ReviewResult], path="review.json"):
    payload = []

    for r in results:
        entry = r.issue.to_dict()
        if r.ai_review:
            entry["ai"] = r.ai_review.to_dict()
        if hasattr(r, "fix"):
            entry["fix"] = r.fix
        payload.append(entry)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
