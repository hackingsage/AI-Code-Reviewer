import { exec } from "child_process";
import * as vscode from "vscode";
import * as fs from "fs";
import * as path from "path";

function computeRange(
  document: vscode.TextDocument,
  line: number,
  snippet?: string
): vscode.Range {
  const textLine = document.lineAt(line - 1).text;

  // Try exact snippet match (best effort)
  if (snippet) {
    const clean = snippet.trim().split("\n")[0];
    const idx = textLine.indexOf(clean);
    if (idx !== -1) {
      return new vscode.Range(
        line - 1,
        idx,
        line - 1,
        idx + clean.length
      );
    }
  }

  // Fallback: underline first meaningful token
  const match = textLine.match(/[A-Za-z_][A-Za-z0-9_]*/);
  if (match && match.index !== undefined) {
    return new vscode.Range(
      line - 1,
      match.index,
      line - 1,
      match.index + match[0].length
    );
  }

  return new vscode.Range(line - 1, 0, line - 1, 1);
}

export function runReview(
  filePath: string,
  diagnostics: vscode.DiagnosticCollection,
  reviewCache: Map<string, { mtime: number; data: any[] }>,
  diagnosticsByFile: Map<string, vscode.Diagnostic[]>
) {
  const uri = vscode.Uri.file(filePath);

  const stat = fs.statSync(filePath);
  const cached = reviewCache.get(filePath);

  // Reuse cached results if unchanged
  if (cached && cached.mtime === stat.mtimeMs) {
    applyDiagnostics(uri, cached.data, diagnostics, diagnosticsByFile);
    vscode.window.setStatusBarMessage(
      "AI Code Review (cached)",
      2000
    );
    return;
  }

  const reviewScript = path.join(
    __dirname,
    "..",
    "..",
    "review.py"
  );

  exec(
    `python "${reviewScript}" "${filePath}" --json`,
    (err, stdout, stderr) => {
      if (err) {
        vscode.window.showErrorMessage("AI Code Review failed");
        console.error(stderr);
        return;
      }

      const jsonPath = path.join(
        path.dirname(reviewScript),
        "review.json"
      );

      if (!fs.existsSync(jsonPath)) {
        vscode.window.showErrorMessage(
          "AI Code Review produced no output"
        );
        return;
      }

      const data = JSON.parse(
        fs.readFileSync(jsonPath, "utf-8")
      );

      reviewCache.set(filePath, {
        mtime: stat.mtimeMs,
        data,
      });

      applyDiagnostics(uri, data, diagnostics, diagnosticsByFile);

      vscode.window.setStatusBarMessage(
        "AI Code Review completed",
        3000
      );
    }
  );
}

function applyDiagnostics(
  uri: vscode.Uri,
  data: any[],
  diagnostics: vscode.DiagnosticCollection,
  diagnosticsByFile: Map<string, vscode.Diagnostic[]>
) {
  const document = vscode.workspace.textDocuments.find(
    d => d.uri.fsPath === uri.fsPath
  );
  if (!document) return;

  const issues: vscode.Diagnostic[] = [];

  for (const item of data) {
    if (!item.line || item.line < 1) continue;

    const range = computeRange(
      document,
      item.line,
      item.code_snippet
    );

    const severity =
      item.severity >= 5
        ? vscode.DiagnosticSeverity.Error
        : item.severity >= 3
        ? vscode.DiagnosticSeverity.Warning
        : vscode.DiagnosticSeverity.Hint;

    const diag = new vscode.Diagnostic(
      range,
      item.message,
      severity
    );

    if (item.fix) {
      console.log("FIX AVAILABLE:", item.fix);
    } else {
      console.log("NO FIX FOR:", item.rule);
    }

    (diag as any).fix = item.fix ?? null;
    issues.push(diag);
  }

  diagnosticsByFile.set(uri.fsPath, issues);
  diagnostics.set(uri, issues);
}
