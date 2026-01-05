import ast
from typing import List, Set
from core.types import Issue

class UnusedVisitor(ast.NodeVisitor):
    def __init__(self):
        self.assigned: Set[str] = set()
        self.used: Set[str] = set()
        self.imports: Set[str] = set()

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.assigned.add(target.id)
        self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.used.add(node.id)

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.add(alias.asname or alias.name.split(".")[0])

    def visit_ImportFrom(self, node):
        for alias in node.names:
            self.imports.add(alias.asname or alias.name)

def analyze(function) -> List[Issue]:
    visitor = UnusedVisitor()
    visitor.visit(function.body)

    issues: List[Issue] = []

    for name in visitor.assigned - visitor.used:
        issues.append(
            Issue(
                line=function.line_no,
                category="maintainability",
                rule="unused_variable",
                message=f"Variable '{name}' is assigned but never used.",
                code_snippet=function.source,
                severity=2,
            )
        )

    for imp in visitor.imports - visitor.used:
        issues.append(
            Issue(
                line=function.line_no,
                category="maintainability",
                rule="unused_import",
                message=f"Imported name '{imp}' is never used.",
                code_snippet=function.source,
                severity=1,
            )
        )

    return issues