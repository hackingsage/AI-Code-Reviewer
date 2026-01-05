import ast
from typing import List
from core.types import Issue

DANGEROUS_CALLS = {
    "eval": 5,
    "exec": 5,
    "compile": 4,
}

DANGEROUS_ATTR_CALLS = {
    ("os", "system"): 5,
    ("subprocess", "Popen"): 4,
    ("subprocess", "call"): 4,
    ("subprocess", "run"): 4,
}

INSECURE_HASHES = {"md5", "sha1"}

DESERIALIZATION_CALLS = {
    ("pickle", "loads"),
    ("pickle", "load"),
    ("yaml", "load"),
}

class SecurityVisitor(ast.NodeVisitor):
    def __init__(self):
        self.issues: List[Issue] = []

    # ---------- Dangerous built-ins ----------

    def visit_Call(self, node: ast.Call):
        # eval(), exec(), compile()
        if isinstance(node.func, ast.Name):
            name = node.func.id
            if name in DANGEROUS_CALLS:
                self.issues.append(
                    Issue(
                        line=node.lineno,
                        category="security",
                        rule=f"use_of_{name}",
                        message=f"Use of '{name}()' can lead to code injection.",
                        code_snippet=ast.unparse(node),
                        severity=DANGEROUS_CALLS[name],
                    )
                )

        # os.system(), subprocess.*
        if isinstance(node.func, ast.Attribute):
            module = self._get_root_name(node.func.value)
            attr = node.func.attr

            if (module, attr) in DANGEROUS_ATTR_CALLS:
                self.issues.append(
                    Issue(
                        line=node.lineno,
                        category="security",
                        rule=f"{module}_{attr}",
                        message=(
                            f"Call to '{module}.{attr}()' may allow command injection "
                            "if input is not sanitized."
                        ),
                        code_snippet=ast.unparse(node),
                        severity=DANGEROUS_ATTR_CALLS[(module, attr)],
                    )
                )

        # Insecure hashing
        if isinstance(node.func, ast.Attribute):
            attr = node.func.attr
            if attr in INSECURE_HASHES:
                self.issues.append(
                    Issue(
                        line=node.lineno,
                        category="security",
                        rule="weak_hash",
                        message=(
                            f"Use of insecure hash function '{attr}'. "
                            "Prefer SHA-256 or stronger."
                        ),
                        code_snippet=ast.unparse(node),
                        severity=3,
                    )
                )

        self.generic_visit(node)

    # ---------- Deserialization ----------

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            if alias.name == "pickle":
                self._warn_import(node, "pickle")

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module == "pickle":
            self._warn_import(node, "pickle")

    def _warn_import(self, node, module: str):
        self.issues.append(
            Issue(
                line=node.lineno,
                category="security",
                rule="unsafe_deserialization",
                message=(
                    f"Importing '{module}' can be unsafe when loading "
                    "untrusted data."
                ),
                code_snippet=module,
                severity=3,
            )
        )

    # ---------- Helpers ----------

    def _get_root_name(self, node):
        while isinstance(node, ast.Attribute):
            node = node.value
        if isinstance(node, ast.Name):
            return node.id
        return None


def analyze(function) -> List[Issue]:
    visitor = SecurityVisitor()
    visitor.visit(function.body)
    return visitor.issues
