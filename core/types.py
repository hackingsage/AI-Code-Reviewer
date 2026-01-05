from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass(frozen=True)
class Issue:
    """
    A deterministic issue produced by a static analyzer.
    LLMs may enhance this, but never redefine it.
    """

    line: int
    category: str              # complexity | performance | patterns | security
    rule: str                  # specific rule identifier
    message: str               # human-readable explanation
    code_snippet: str           # exact source snippet
    severity: int               # 1 (low) → 5 (critical)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "line": self.line,
            "category": self.category,
            "rule": self.rule,
            "message": self.message,
            "code_snippet": self.code_snippet,
            "severity": self.severity,
        }


@dataclass
class AIReview:
    """
    LLM-generated enrichment of an Issue.
    This is optional and should never block execution.
    """

    explanation: str
    suggestion: str
    confidence: float          # 0.0 → 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "explanation": self.explanation,
            "suggestion": self.suggestion,
            "confidence": self.confidence,
        }


@dataclass
class ReviewResult:
    """
    Final output object combining static issues and optional AI feedback.
    """

    issue: Issue
    ai_review: Optional[AIReview] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "issue": self.issue.to_dict(),
        }
        if self.ai_review:
            result["ai_review"] = self.ai_review.to_dict()
        return result
