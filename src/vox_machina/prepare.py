"""Download and verify all required models."""

import logging

from rich.console import Console
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TransferSpeedColumn,
)

from vox_machina.config import VoxConfig


logger = logging.getLogger(__name__)
console = Console()


def prepare_whisper(config: VoxConfig) -> bool:
    """Download the configured whisper model."""
    model = config.whisper_model
    console.print(f"\n[bold]Whisper model:[/bold] {model}")

    try:
        from faster_whisper import download_model

        with Progress(
            SpinnerColumn(),
            TextColumn(f"[blue]Downloading whisper {model}..."),
        ) as progress:
            progress.add_task("downloading", total=None)
            download_model(model)

        console.print("  [green]Ready.[/green]")
        return True
    except Exception:
        logger.exception("Failed to download whisper model")
        console.print(f"  [red]Failed to download whisper model '{model}'.[/red]")
        return False


def prepare_diarization() -> bool:
    """Download the pyannote diarization model."""
    from vox_machina.diarize import DIARIZATION_MODEL

    console.print(f"\n[bold]Diarization model:[/bold] {DIARIZATION_MODEL}")

    try:
        from pyannote.audio import Pipeline

        with Progress(
            SpinnerColumn(),
            TextColumn("[blue]Downloading diarization model..."),
        ) as progress:
            progress.add_task("downloading", total=None)
            pipeline = Pipeline.from_pretrained(DIARIZATION_MODEL)

        if pipeline is None:
            console.print(
                "  [red]Failed to load diarization model. Check HuggingFace login.[/red]"
            )
            return False

        console.print("  [green]Ready.[/green]")
        return True
    except Exception:
        logger.exception("Failed to download diarization model")
        console.print(
            "  [red]Failed to download diarization model. "
            "Run 'uv run hf auth login' first.[/red]"
        )
        return False


def prepare_ollama(config: VoxConfig) -> bool:
    """Pull the configured Ollama model."""
    model = config.ollama_model
    console.print(f"\n[bold]Ollama model:[/bold] {model}")

    try:
        import ollama

        with Progress(
            SpinnerColumn(),
            TextColumn(f"[blue]Pulling {model}..."),
            BarColumn(),
            DownloadColumn(),
            TransferSpeedColumn(),
        ) as progress:
            task = None
            for update in ollama.pull(model, stream=True):
                status = update.status or ""
                if update.total and update.completed is not None:
                    if task is None:
                        task = progress.add_task(status, total=update.total)
                    progress.update(
                        task, completed=update.completed, description=status
                    )
                elif task is None:
                    task = progress.add_task(status, total=None)

        console.print("  [green]Ready.[/green]")
        return True
    except Exception:
        logger.exception("Failed to pull ollama model")
        console.print(
            f"  [red]Failed to pull '{model}'. "
            "Make sure Ollama is running: ollama serve[/red]"
        )
        return False


def prepare_all(config: VoxConfig) -> None:
    """Download all required models."""
    console.print("[bold]Preparing vox-machina models...[/bold]")

    results = [
        ("Whisper", prepare_whisper(config)),
        ("Diarization", prepare_diarization()),
        ("Ollama", prepare_ollama(config)),
    ]

    console.print()
    all_ok = all(ok for _, ok in results)
    if all_ok:
        console.print("[bold green]All models ready.[/bold green]")
    else:
        failed = [name for name, ok in results if not ok]
        console.print(f"[bold red]Failed: {', '.join(failed)}[/bold red]")
