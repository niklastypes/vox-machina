import collections.abc
from importlib.resources import files
from pathlib import Path

import ollama
from jinja2 import BaseLoader, Environment, TemplateNotFound
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn


class _BuiltinPromptLoader(BaseLoader):
    """Jinja2 loader that reads from the bundled prompts package."""

    def get_source(
        self, environment: Environment, template: str
    ) -> tuple[str, str, collections.abc.Callable[[], bool]]:
        prompts_dir = files("vox_machina.prompts")
        resource = prompts_dir.joinpath(template)
        if not resource.is_file():
            raise TemplateNotFound(template)
        source = resource.read_text()
        return source, template, lambda: True


_jinja_env = Environment(loader=_BuiltinPromptLoader(), keep_trailing_newline=True)


def list_builtin_prompts() -> list[str]:
    """List names of built-in prompt templates (without extension)."""
    prompts_dir = files("vox_machina.prompts")
    return sorted(
        p.name.removesuffix(".md.j2")
        for p in prompts_dir.iterdir()  # type: ignore[union-attr]
        if hasattr(p, "name")
        and p.name.endswith(".md.j2")
        and not p.name.startswith("base")
    )


def render_prompt(prompt: str | None, transcript: str) -> str:
    """Render a prompt template with the transcript injected.

    Resolution order:
    1. None -> default (meeting_notes)
    2. Built-in name (e.g. "standup") -> bundled Jinja2 template
    3. File path -> read from disk as plain template with {transcript} placeholder
    """
    if prompt is None:
        prompt = "meeting_notes"

    # Try built-in Jinja2 template
    template_name = f"{prompt}.md.j2"
    try:
        template = _jinja_env.get_template(template_name)
        return template.render(transcript=transcript)
    except TemplateNotFound:
        pass

    # Fall back to file path (plain template with {transcript} placeholder)
    path = Path(prompt)
    if path.is_file():
        return path.read_text().replace("{transcript}", transcript)

    available = ", ".join(list_builtin_prompts())
    msg = f"Prompt '{prompt}' not found. Built-in prompts: {available}"
    raise FileNotFoundError(msg)


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
    prompt_name: str | None = None,
) -> str:
    verify_model_available(model)

    prompt = render_prompt(prompt_name, transcript)

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
