import { exec } from "child_process";
import * as vscode from "vscode";
import * as fs from "fs";
import * as path from "path";

function computeRange(
  document: vscode.TextDocument,
  line: number,
  snippet: string
): vscode.Range {
  const textLine = document.lineAt(line - 1).text;

  const idx = textLine.indexOf(snippet.trim());

  if (idx !== -1) {
    return new vscode.Range(
      line - 1,
      idx,
      line - 1,
      idx + snippet.trim().length
    );
  }

  // fallback: underline first token
  return new vscode.Range(
    line - 1,
    0,
    line - 1,
    Math.min(textLine.length, 80)
  );
}


export function runReview(
  filePath: string,
  diagnostics: vscode.DiagnosticCollection,
  reviewCache: Map<string, { mtime: number; data: any[] }>
) {
  const uri = vscode.Uri.file(filePath);

  // Clear previous diagnostics
  diagnostics.delete(uri);

  const stat = fs.statSync(filePath);
  const cached = reviewCache.get(filePath);

  // Use cache if file unchanged
  if (cached && cached.mtime === stat.mtimeMs) {
    applyDiagnostics(uri, cached.data, diagnostics);
    vscode.window.setStatusBarMessage(
      "AI Code Review (cached)",
      2000
    );
    return;
  }

  // Absolute path to review.py (VS Code safe)
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

      applyDiagnostics(uri, data, diagnostics);

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
  diagnostics: vscode.DiagnosticCollection
) {
  const issues: vscode.Diagnostic[] = [];

  for (const item of data) {
    if (!item.line || item.line < 1) continue;

    const range = computeRange(
      vscode.window.activeTextEditor!.document,
      item.line,
      item.code_snippet ?? ""
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

    // Attach fix safely (may be null)
    (diag as any).fix = item.fix ?? null;

    issues.push(diag);
  }

  diagnostics.set(uri, issues);
}
