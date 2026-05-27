from importlib.resources import files
from pathlib import Path

import ollama
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn


def load_prompt_template(prompt_path: str | None = None) -> str:
    if prompt_path:
        return Path(prompt_path).read_text()
    default = files("vox_machina.prompts").joinpath("meeting_notes.md")
    return default.read_text()


def build_prompt(template: str, transcript: str) -> str:
    return template.replace("{transcript}", transcript)


def verify_model_available(model: str) -> None:
    """Check that the requested Ollama model is pulled locally."""
    console = Console()
    try:
        response = ollama.list()
        available = [m.model for m in response.models if m.model]
        # Match both "model:tag" and bare "model" against the requested name
        if not any(model == m or m.startswith(f"{model}:") for m in available):
            console.print(
                f"[red]Error: model '{model}' not found locally. "
                f"Pull it first with: ollama pull {model}[/red]"
            )
            console.print(
                f"[dim]Available models: {', '.join(available) or '(none)'}[/dim]"
            )
            raise SystemExit(1)
    except ConnectionError:
        console.print(
            "[red]Error: cannot connect to Ollama. "
            "Make sure it is running: ollama serve[/red]"
        )
        raise SystemExit(1) from None


def _estimate_num_ctx(prompt: str) -> int:
    """Estimate required context window size from prompt length."""
    estimated_tokens = len(prompt) // 4
    return max(2048, estimated_tokens + 1024)


def summarize_transcript(
    transcript: str,
    model: str = "qwen3.5:9b",
    prompt_path: str | None = None,
) -> str:
    verify_model_available(model)

    template = load_prompt_template(prompt_path)
    prompt = build_prompt(template, transcript)

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]Summarizing with Ollama..."),
    ) as progress:
        progress.add_task("summarizing", total=None)
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            options={"num_ctx": _estimate_num_ctx(prompt)},
        )

    return response.message.content or ""
