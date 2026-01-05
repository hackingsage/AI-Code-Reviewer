import * as vscode from "vscode";
import { runReview } from "./runner";

// In-memory cache shared with runner
export const reviewCache = new Map<
  string,
  { mtime: number; data: any[] }
>();

export function activate(context: vscode.ExtensionContext) {
  const diagnostics =
    vscode.languages.createDiagnosticCollection("ai-review");

  context.subscriptions.push(diagnostics);

  // Run review command
  context.subscriptions.push(
    vscode.commands.registerCommand("aiReview.run", () => {
      const editor = vscode.window.activeTextEditor;
      if (!editor) return;

      runReview(
        editor.document.fileName,
        diagnostics,
        reviewCache
      );
    })
  );

  // Clear diagnostics + cache on save
  context.subscriptions.push(
    vscode.workspace.onDidSaveTextDocument(doc => {
      diagnostics.delete(doc.uri);
      reviewCache.delete(doc.fileName);
    })
  );

  // Code action provider (Accept AI fix)
  context.subscriptions.push(
    vscode.languages.registerCodeActionsProvider(
      ["python"],
      {
        provideCodeActions(document, range, context) {
          const actions: vscode.CodeAction[] = [];

          for (const diag of context.diagnostics) {
            const fix = (diag as any).fix;
            if (!fix) continue;

            // Only show action if cursor overlaps diagnostic
            if (!diag.range.intersection(range)) continue;

            const action = new vscode.CodeAction(
              "AI: Apply suggested fix",
              vscode.CodeActionKind.QuickFix
            );

            action.command = {
              command: "aiReview.applyFix",
              title: "Apply AI Fix",
              arguments: [document.uri, diag.range, fix],
            };

            actions.push(action);
          }

          return actions;
        },
      },
      {
        providedCodeActionKinds: [vscode.CodeActionKind.QuickFix],
      }
    )
  );

  // Apply fix safely (diff + undo handled by VS Code)
  context.subscriptions.push(
    vscode.commands.registerCommand(
      "aiReview.applyFix",
      (uri: vscode.Uri, range: vscode.Range, fix: string) => {
        const edit = new vscode.WorkspaceEdit();
        edit.replace(uri, range, fix);
        vscode.workspace.applyEdit(edit);
      }
    )
  );
}

export function deactivate() {}
