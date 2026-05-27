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
        available = [m.model for m in response.models]
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


def check_context_window(prompt: str, model: str) -> None:
    """Warn if the prompt is likely too large for the model's context window."""
    estimated_tokens = len(prompt) // 4
    try:
        model_info = ollama.show(model)
        num_ctx = int(model_info.get("parameters", {}).get("num_ctx", 2048))
    except Exception:
        num_ctx = 2048

    if estimated_tokens > num_ctx:
        console = Console()
        console.print(
            f"[yellow]Warning: transcript is ~{estimated_tokens} tokens, "
            f"but {model}'s context window is {num_ctx} tokens. "
            f"Consider increasing num_ctx in your Ollama modelfile.[/yellow]"
        )


def summarize_transcript(
    transcript: str,
    model: str = "llama3.1",
    prompt_path: str | None = None,
) -> str:
    verify_model_available(model)

    template = load_prompt_template(prompt_path)
    prompt = build_prompt(template, transcript)

    check_context_window(prompt, model)

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]Summarizing with Ollama..."),
    ) as progress:
        progress.add_task("summarizing", total=None)
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )

    return response.message.content
