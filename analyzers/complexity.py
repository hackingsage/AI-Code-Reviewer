import ast
from typing import List
from core.types import Issue

class ComplexityVisitor(ast.NodeVisitor):
    def __init__(self):
        self.current_depth = 0
        self.max_depth = 0
        self.loop_count = 0

    # ---------- Loop tracking ----------

    def visit_For(self, node: ast.For):
        self._enter_loop(node)

    def visit_While(self, node: ast.While):
        self._enter_loop(node)

    def _enter_loop(self, node):
        self.loop_count += 1
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1

    # ---------- Conditionals (affect complexity but not big-O) ----------

    def visit_If(self, node: ast.If):
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1


def analyze(function) -> List[Issue]:
    """
    Analyze a ParsedFunction for complexity issues.
    """
    visitor = ComplexityVisitor()
    visitor.visit(function.body)

    issues: List[Issue] = []

    # Heuristic: nested loops → likely O(n^2) or worse
    if visitor.max_depth >= 2 and visitor.loop_count >= 2:
        issues.append(
            Issue(
                line=function.line_no,
                category="complexity",
                rule="nested_loops",
                message=(
                    f"Function '{function.name}' contains nested loops "
                    f"(max depth = {visitor.max_depth}). "
                    "This may lead to quadratic or worse time complexity."
                ),
                code_snippet=function.source,
                severity=min(visitor.max_depth, 5),
            )
        )

    # Heuristic: very deep nesting hurts readability
    if visitor.max_depth >= 4:
        issues.append(
            Issue(
                line=function.line_no,
                category="complexity",
                rule="deep_nesting",
                message=(
                    f"Function '{function.name}' has deep control-flow nesting "
                    f"(depth = {visitor.max_depth}). Consider refactoring."
                ),
                code_snippet=function.source,
                severity=3,
            )
        )

    return issues
