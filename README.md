---
# AI Powered Code Review (Local, VS Code)

A **local, production-oriented AI-assisted code review tool** that combines **deterministic static analysis** with **optional AI recommendations**, fully integrated into **VS Code**.

> ✅ Works offline  
> ✅ No cloud APIs  
> ✅ No auto-modifying code  
> ✅ AI never blocks correctness  

---

## ✨ What This Project Does

- Runs **fast static analysis** on Python code
- Detects:
  - Security issues
  - Bug-prone logic
  - Performance anti-patterns
  - Complexity & maintainability issues
- Optionally enriches findings with **AI explanations and fixes**
- Integrates directly into **VS Code**
- Provides **safe, human-in-the-loop fixes** (Accept / Reject with diff)

This tool is designed with **production principles**, not as a demo.

---

## 🎯 Key Features

### 🔍 Static Analysis (Always Fast, Always Correct)
- AST-based analysis
- Deterministic results
- Instant diagnostics
- Independent of AI speed

### 🤖 AI Assistance (Optional)
- Local LLM via **Ollama**
- Explains issues in plain language
- Suggests fixes when confident
- AI failures never crash the tool

### 🧠 Safe Fix Workflow
- Fixes are **never auto-applied**
- VS Code diff preview
- One-click **Accept / Reject**
- Full undo support
---

## 🏗 Architecture Overview

```

VS Code Extension
│
▼
review.py (Python CLI)
├── Static Analyzers (fast)
├── AI Enrichment (slow, optional)
└── JSON contract
│
▼
VS Code Diagnostics + Code Actions

```

**Design rule:**
> Static analysis defines truth.  
> AI only augments, never blocks.

---

## 📂 Repository Structure

```

ai-powered-code-review/
├── analyzers/        # Static analysis rules
├── core/             # Parsing, types, context
├── llm/              # LLM client & prompts
├── samples/          # Test & demo files
├── vscode-extension/ # VS Code extension
├── review.py         # Main CLI entrypoint
├── requirements.txt
└── README.md

````

---

## 🚀 Getting Started

### Requirements
- Python **3.10+**
- Node.js **LTS**
- VS Code
- Ollama

---

### 1️⃣ Install Python dependencies

```bash
pip install -r requirements.txt
````

---

### 2️⃣ Start Ollama & pull a model

```bash
ollama serve
ollama pull deepseek-coder:6.7b
```

> 💡 On CPU-only machines, smaller models work faster.

---

### 3️⃣ Run the VS Code extension

```bash
cd vscode-extension
npm install
npm run compile
```

Press **F5** to launch the Extension Development Host.

---

### 4️⃣ Use the tool

1. Open a Python file
2. Press `Ctrl + Shift + P`
3. Run:

   * **AI Code Review: Static Analysis** (fast)
   * **AI Code Review: With AI** (slow, optional)

---

## 🧪 Example

```python
def run(x):
    return eval(x)
```

**Result in VS Code:**

* ❗ Security warning underlined
* 💡 “AI: Apply suggested fix”
* 🔍 Diff preview
* ✅ Accept or ❌ Reject

---

## 🧠 Design Philosophy

* AI output is **untrusted**
* Static analysis is **authoritative**
* No silent code changes
* Deterministic behavior first
* Designed for real-world usage

This mirrors how **production developer tools** are built.

---

## 📦 What This Project Is (and Isn’t)

✅ A real developer tool
✅ Local & privacy-preserving
✅ Extensible architecture
❌ Not a Copilot replacement
❌ Not cloud-dependent

---

## 🔮 Future Work (Optional)

* GitHub PR review bot (reuse same pipeline)
* Configurable rules via `.ai-review.yml`
* Additional language support
* Packaged VS Code extension

---

## 📄 License

MIT