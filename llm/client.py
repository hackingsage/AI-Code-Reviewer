import ast
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

        raw = self.model_call(
            prompt=FIX_PROMPT.format(code=issue.code_snippet),
            system=SYSTEM_PROMPT,
        )

        if not raw:
            return None

        # 1️⃣ Extract JSON object (best-effort)
        match = re.search(r"\{[\s\S]*?\}", raw)
        if not match:
            return None

        json_text = match.group(0)

        # 2️⃣ Try to parse JSON
        try:
            data = json.loads(json_text)
        except json.JSONDecodeError:
            return None

        expr = data.get("fixed_expression")
        if not isinstance(expr, str):
            return None

        expr = expr.strip()

        # 3️⃣ HARD SAFETY CHECKS

        # Single expression only
        try:
            tree = ast.parse(expr, mode="eval")
        except SyntaxError:
            return None

        # No imports
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                return None

        # No function / class definitions
        if any(isinstance(node, (ast.FunctionDef, ast.ClassDef)) for node in ast.walk(tree)):
            return None

        # No multiline replacements
        if "\n" in expr or len(expr) > 80:
            return None

        return expr



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
