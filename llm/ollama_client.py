import subprocess

OLLAMA_PATH = "PATH_TO_OLLAMA"

def ollama_call(prompt: str, system: str, model: str = "deepseek-coder:6.7b") -> str:
    full_prompt = f"{system}\n\n{prompt}"

    completed = subprocess.run(
        [OLLAMA_PATH, "run", model],
        input=full_prompt,
        text=True,
        encoding="utf-8",      
        errors="replace",      
        capture_output=True,
    )

    if completed.returncode != 0:
        raise RuntimeError(
            f"Ollama failed:\n{completed.stderr}"
        )

    return completed.stdout.strip()
