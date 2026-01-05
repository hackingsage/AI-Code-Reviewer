import ast
from typing import List, Set
from core.types import Issue

BUILTINS: Set[str] = {
    "list", "dict", "set", "tuple", "str", "int", "float",
    "bool", "len", "sum", "max", "min", "map", "filter",
    "open", "range", "print"
}

class PatternVisitor(ast.NodeVisitor):
    def __init__(self):
        self.issues: List[Issue] = []
        self.assigned_names: Set[str] = set()
        self.used_names: Set[str] = set()

    # ---------- Function-level patterns ----------

    def visit_FunctionDef(self, node: ast.FunctionDef):
        # Mutable default arguments
        for arg, default in zip(
            reversed(node.args.args),
            reversed(node.args.defaults),
        ):
            if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                self.issues.append(
                    Issue(
                        line=default.lineno,
                        category="patterns",
                        rule="mutable_default_argument",
                        message=(
                            f"Mutable default argument '{arg.arg}' in function "
                            f"'{node.name}'. This can cause shared state bugs."
                        ),
                        code_snippet=ast.unparse(default),
                        severity=4,
                    )
                )

        self.generic_visit(node)

    # ---------- Exception handling ----------

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        if node.type is None:
            self.issues.append(
                Issue(
                    line=node.lineno,
                    category="patterns",
                    rule="bare_except",
                    message="Bare except detected. This can hide critical errors.",
                    code_snippet="except:",
                    severity=3,
                )
            )
        self.generic_visit(node)

    # ---------- Name tracking ----------

    def visit_Assign(self, node: ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.assigned_names.add(target.id)

                # Shadowing built-ins
                if target.id in BUILTINS:
                    self.issues.append(
                        Issue(
                            line=target.lineno,
                            category="patterns",
                            rule="shadow_builtin",
                            message=(
                                f"Variable '{target.id}' shadows a Python built-in."
                            ),
                            code_snippet=ast.unparse(node),
                            severity=2,
                        )
                    )

        self.generic_visit(node)

    def visit_Name(self, node: ast.Name):
        if isinstance(node.ctx, ast.Load):
            self.used_names.add(node.id)

    # ---------- Final pass ----------

    def finalize(self):
        # Unused variables
        unused = self.assigned_names - self.used_names
        for name in unused:
            self.issues.append(
                Issue(
                    line=0,
                    category="patterns",
                    rule="unused_variable",
                    message=f"Variable '{name}' is assigned but never used.",
                    code_snippet=name,
                    severity=1,
                )
            )


def analyze(function) -> List[Issue]:
    visitor = PatternVisitor()
    visitor.visit(function.body)
    visitor.finalize()
    return visitor.issues
