import subprocess

"""
Kindly add OLLAMA_PATH to your ollama.exe and also select the
model you wanna work with.
"""


# OLLAMA_PATH = "PATH_TO_OLLAMA"
OLLAMA_PATH = r"C:\\Users\\Arul\AppData\\Local\\Programs\\Ollama\\ollama.exe"

def ollama_call(prompt: str, system: str, model: str = "MODEL") -> str:
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
