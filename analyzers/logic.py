import ast
from typing import List
from core.types import Issue

class LogicVisitor(ast.NodeVisitor):
    def __init__(self):
        self.issues: List[Issue] = []

    def visit_Compare(self, node):
        for op, comparator in zip(node.ops, node.comparators):
            if isinstance(comparator, ast.Constant) and comparator.value is None:
                if isinstance(op, ast.Eq):
                    self.issues.append(
                        Issue(
                            line=node.lineno,
                            category="bug",
                            rule="compare_none",
                            message="Use 'is None' instead of '== None'.",
                            code_snippet=ast.unparse(node),
                            severity=3,
                        )
                    )
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        for default in node.args.defaults:
            if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                self.issues.append(
                    Issue(
                        line=node.lineno,
                        category="bug",
                        rule="mutable_default",
                        message="Mutable default argument can cause shared state bugs.",
                        code_snippet=ast.unparse(node),
                        severity=4,
                    )
                )
        self.generic_visit(node)

def analyze(function) -> List[Issue]:
    visitor = LogicVisitor()
    visitor.visit(function.body)
    return visitor.issues
