SYSTEM_PROMPT = """You are a senior software engineer performing a strict code review.

Rules:
- Only explain the issue provided.
- Do NOT invent new bugs.
- Do NOT speculate.
- Base all reasoning strictly on the given code snippet.
- If the issue is minor, say so.
"""

FIX_PROMPT = """
You are reviewing Python code.

RULES (STRICT):
- You may ONLY replace the expression that contains the bug.
- Do NOT add imports.
- Do NOT add new statements.
- Do NOT modify function signatures.
- Output MUST be a single valid Python expression.
- Do NOT include explanations.
- Do NOT include markdown.

Given this buggy expression:
{code}

Return JSON exactly in this form:
{{
  "fixed_expression": "<single Python expression>"
}}
"""



REVIEW_PROMPT = """
You are given a code issue detected by a static analyzer.

Issue category: {category}
Rule: {rule}
Severity (1-5): {severity}

Message:
{message}

Code snippet:
{code}

Tasks:
1. Explain clearly why this is a problem.
2. Suggest a concrete fix or refactor.
3. Rate your confidence in this suggestion from 0.0 to 1.0.

Respond ONLY in valid JSON with the following format:
{{
  "explanation": "...",
  "suggestion": "...",
  "confidence": 0.0
}}
"""
