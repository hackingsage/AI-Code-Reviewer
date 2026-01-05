import ast
from typing import List
from core.types import Issue

def analyze(function) -> List[Issue]:
    issues: List[Issue] = []

    if function.source.count("\n") > 50:
        issues.append(
            Issue(
                line=function.line_no,
                category="maintainability",
                rule="long_function",
                message="Function is very long; consider refactoring.",
                code_snippet=function.source,
                severity=2,
            )
        )

    if len(function.args) > 5:
        issues.append(
            Issue(
                line=function.line_no,
                category="maintainability",
                rule="many_parameters",
                message="Function has many parameters; consider grouping them.",
                code_snippet=function.source,
                severity=2,
            )
        )

    return issues
