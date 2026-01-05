import ast
from typing import List
from core.types import Issue

class PerformanceVisitor(ast.NodeVisitor):
    def __init__(self):
        self.loop_depth = 0
        self.issues: List[Issue] = []

    def visit_For(self, node):
        self.loop_depth += 1
        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_While(self, node):
        self.loop_depth += 1
        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_Call(self, node):
        if self.loop_depth > 0:
            if isinstance(node.func, ast.Name) and node.func.id == "len":
                self.issues.append(
                    Issue(
                        line=node.lineno,
                        category="performance",
                        rule="len_in_loop",
                        message="Calling len() inside a loop may be inefficient.",
                        code_snippet=ast.unparse(node),
                        severity=2,
                    )
                )
        self.generic_visit(node)

def analyze(function) -> List[Issue]:
    visitor = PerformanceVisitor()
    visitor.visit(function.body)
    return visitor.issues
