import ast
from typing import List, Dict, Any

class ParsedFunction:
    def __init__(
        self,
        name: str,
        line_no: int,
        end_line_no: int,
        args: List[str],
        body: ast.AST,
        source: str,
    ):
        self.name = name
        self.line_no = line_no
        self.end_line_no = end_line_no
        self.args = args
        self.body = body
        self.source = source

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "line_no": self.line_no,
            "end_line_no": self.end_line_no,
            "args": self.args,
            "source": self.source,
        }


class CodeParser(ast.NodeVisitor):
    def __init__(self, source_code: str):
        self.source_code = source_code
        self.tree = ast.parse(source_code)
        self.lines = source_code.splitlines()
        self.functions: List[ParsedFunction] = []
        self.imports: List[str] = []

    def parse(self):
        self.visit(self.tree)
        return {
            "functions": self.functions,
            "imports": self.imports,
        }

    # ---------- Visitors ----------

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._handle_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self._handle_function(node)
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self.imports.append(alias.name)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        module = node.module or ""
        for alias in node.names:
            full_name = f"{module}.{alias.name}" if module else alias.name
            self.imports.append(full_name)

    # ---------- Helpers ----------

    def _handle_function(self, node: ast.AST):
        name = node.name
        line_no = node.lineno
        end_line_no = getattr(node, "end_lineno", line_no)

        args = [arg.arg for arg in node.args.args]

        source = self._extract_source(line_no, end_line_no)

        parsed_fn = ParsedFunction(
            name=name,
            line_no=line_no,
            end_line_no=end_line_no,
            args=args,
            body=node,
            source=source,
        )

        self.functions.append(parsed_fn)

    def _extract_source(self, start: int, end: int) -> str:
        # AST line numbers are 1-based
        return "\n".join(self.lines[start - 1 : end])


# ---------- Public API ----------

def parse_file(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    parser = CodeParser(source)
    return parser.parse()
