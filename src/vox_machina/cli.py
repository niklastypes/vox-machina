"""Shared CLI helpers used by both vox and machina apps."""

from pathlib import Path

import questionary
from rich.console import Console

from vox_machina.banner import print_banner
from vox_machina.config import (
    DEFAULT_OLLAMA_MODEL,
    DEFAULT_WHISPER_MODEL,
    VoxConfig,
    config_exists,
    load_config,
    save_config,
)


INITIAL_QUOTES = 3
WHISPER_MODELS = ["small", "medium", "large-v3"]

console = Console()


def banner_callback(ctx, app_name: str) -> None:
    """Show banner and help hint when no subcommand is given."""
    print_banner()
    if ctx.invoked_subcommand is None:
        console.print(f"Run [bold]{app_name} --help[/bold] for usage information.")
        raise SystemExit(0)


def require_md(file: Path) -> None:
    if file.suffix.lower() != ".md":
        console.print(f"[red]Error: expected a .md file, got {file.suffix}[/red]")
        raise SystemExit(1)


def list_ollama_models() -> list[str]:
    """List locally available Ollama models."""
    try:
        import ollama

        response = ollama.list()
        return [m.model for m in response.models if m.model]
    except Exception:
        return []


def run_config_questionnaire() -> VoxConfig:
    """Interactive configuration setup."""
    console.print("\n[bold]First-time setup[/bold]\n")

    whisper_model = questionary.select(
        "Whisper model for transcription:",
        choices=[
            questionary.Choice(
                f"{m} (recommended)" if m == DEFAULT_WHISPER_MODEL else m,
                value=m,
            )
            for m in WHISPER_MODELS
        ],
        default=DEFAULT_WHISPER_MODEL,
    ).ask()

    available = list_ollama_models()
    if available:
        choices = [
            questionary.Choice(
                f"{m} (recommended)" if m.startswith(DEFAULT_OLLAMA_MODEL) else m,
                value=m,
            )
            for m in available
        ]
        ollama_model = questionary.select(
            "Ollama model for summarization:",
            choices=choices,
        ).ask()
    else:
        console.print(
            "[yellow]No Ollama models found locally. "
            f"Using default: {DEFAULT_OLLAMA_MODEL}[/yellow]"
        )
        ollama_model = DEFAULT_OLLAMA_MODEL

    config = VoxConfig(
        whisper_model=whisper_model or DEFAULT_WHISPER_MODEL,
        ollama_model=ollama_model or DEFAULT_OLLAMA_MODEL,
    )
    save_config(config)
    console.print("\n[green]Config saved.[/green]")
    return config


def ensure_config() -> VoxConfig:
    """Load config, running the questionnaire on first use."""
    if not config_exists():
        return run_config_questionnaire()
    return load_config()


def prompt_for_speaker_name(speaker: str, quotes: list[str]) -> str | None:
    shown = INITIAL_QUOTES
    while True:
        preview = quotes[:shown]
        lines = [f'  - "{q}"' for q in preview]
        remaining = len(quotes) - shown

        console.print(f"\n[bold]{speaker}[/bold] said:")
        for line in lines:
            console.print(f"[dim]{line}[/dim]")

        if remaining > 0:
            choice = questionary.select(
                "Who is this?",
                choices=[
                    questionary.Choice("Enter name", value="name"),
                    questionary.Choice(
                        f"Show more quotes ({remaining} remaining)", value="more"
                    ),
                    questionary.Choice("Skip", value="skip"),
                ],
            ).ask()

            if choice == "more":
                shown += INITIAL_QUOTES
                continue
            if choice == "skip":
                return None
            return questionary.text("Name:").ask() or None
        else:
            return questionary.text("Who is this?").ask() or None


def config_command() -> None:
    """Configure default models for transcription and summarization."""
    if config_exists():
        cfg = load_config()
        console.print("\n[bold]Current configuration:[/bold]")
        console.print(f"  Whisper model: [bold]{cfg.whisper_model}[/bold]")
        console.print(f"  Ollama model:  [bold]{cfg.ollama_model}[/bold]")
        reconfigure = questionary.confirm("\nReconfigure?", default=False).ask()
        if not reconfigure:
            return

    cfg = run_config_questionnaire()
    console.print(f"\n  Whisper model: [bold]{cfg.whisper_model}[/bold]")
    console.print(f"  Ollama model:  [bold]{cfg.ollama_model}[/bold]")
