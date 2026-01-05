import * as vscode from "vscode";
import { runReview } from "./runner";

// Cache: file → diagnostics
const diagnosticsByFile = new Map<string, vscode.Diagnostic[]>();

// Cache: file → analysis result
const reviewCache = new Map<
  string,
  { mtime: number; data: any[] }
>();

export function activate(context: vscode.ExtensionContext) {
  const diagnostics =
    vscode.languages.createDiagnosticCollection("ai-review");

  context.subscriptions.push(diagnostics);

  // Run static + AI review
  context.subscriptions.push(
    vscode.commands.registerCommand("aiReview.run", () => {
      const editor = vscode.window.activeTextEditor;
      if (!editor) return;

      runReview(
        editor.document.fileName,
        diagnostics,
        reviewCache,
        diagnosticsByFile
      );
    })
  );

  // Apply AI fix (surgical removal)
  context.subscriptions.push(
    vscode.commands.registerCommand(
      "aiReview.applyFix",
      async (uri: vscode.Uri, range: vscode.Range, fix: string) => {
        // 🔒 Guardrails — NEVER trust AI blindly
        if (
          !fix ||
          fix.includes("\n") ||          // no multi-line edits
          fix.length > 100               // no large rewrites
        ) {
          vscode.window.showWarningMessage(
            "AI fix was rejected: unsafe or too large"
          );
          return;
        }

        // Extra safety: do not allow imports
        if (/\bimport\b/.test(fix)) {
          vscode.window.showWarningMessage(
            "AI fix was rejected: contains import"
          );
          return;
        }

        const edit = new vscode.WorkspaceEdit();
        edit.replace(uri, range, fix);

        const applied = await vscode.workspace.applyEdit(edit);
        if (!applied) return;

        // 🧠 Remove ONLY the fixed diagnostic
        const existing = diagnosticsByFile.get(uri.fsPath);
        if (!existing) return;

        const remaining = existing.filter(
          d => !d.range.intersection(range)
        );

        diagnosticsByFile.set(uri.fsPath, remaining);
        diagnostics.set(uri, remaining);
      }
    )
  );


  // Code actions provider
  context.subscriptions.push(
    vscode.languages.registerCodeActionsProvider(
      ["python"],
      {
        provideCodeActions(document, range, ctx) {
          const actions: vscode.CodeAction[] = [];

          for (const diag of ctx.diagnostics) {
            const fix = (diag as any).fix;
            if (!fix) continue;
            if (!diag.range.intersection(range)) continue;

            const action = new vscode.CodeAction(
              "Code Review: Apply Suggested Fix",
              vscode.CodeActionKind.QuickFix
            );

            action.command = {
              command: "aiReview.applyFix",
              title: "AI Apply Fix",
              arguments: [document.uri, diag.range, fix],
            };

            actions.push(action);
          }

          return actions;
        },
      },
      { providedCodeActionKinds: [vscode.CodeActionKind.QuickFix] }
    )
  );

  // IMPORTANT: do NOT clear diagnostics on save
  context.subscriptions.push(
    vscode.workspace.onDidSaveTextDocument(doc => {
      reviewCache.delete(doc.fileName);
    })
  );
}

export function deactivate() {}
