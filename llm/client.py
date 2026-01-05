import json
import re
from typing import Optional
from core.types import Issue, AIReview
from llm.prompts import SYSTEM_PROMPT, REVIEW_PROMPT, FIX_PROMPT

class LLMClient:

    def __init__(self, model_call):
        """
        model_call(prompt: str, system: str) -> str
        """
        self.model_call = model_call

    def generate_fix(self, issue):
        prompt = FIX_PROMPT.format(
            code=issue.code_snippet,
            message=issue.message,
        )

        try:
            raw = self.model_call(prompt=prompt, system=SYSTEM_PROMPT)
            match = re.search(r"\{.*\}", raw, re.S)
            if not match:
                return None

            data = json.loads(match.group())
            fixed_code = data.get("fixed_code")

            if not fixed_code:
                return None
            return fixed_code.strip()

        except Exception:
            return None


    def review_issue(self, issue):
        prompt = REVIEW_PROMPT.format(
            code=issue.code_snippet,
            message=issue.message,
            category=issue.category,
            rule=issue.rule,
            severity=issue.severity,
        )

        try:
            raw = self.model_call(prompt=prompt, system=SYSTEM_PROMPT)
            match = re.search(r"\{.*\}", raw, re.S)
            if not match:
                return None

            data = json.loads(match.group())

            explanation = data.get("explanation")
            suggestion = data.get("suggestion")
            confidence = data.get("confidence")

            if not explanation or not suggestion:
                return None

            try:
                confidence = float(confidence)
                confidence = max(0.0, min(confidence, 1.0))
            except Exception:
                confidence = 0.0

            return AIReview(
                explanation=explanation.strip(),
                suggestion=suggestion.strip(),
                confidence=confidence,
            )

        except Exception:
            raise Exception
