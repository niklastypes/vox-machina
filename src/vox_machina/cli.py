from pathlib import Path
from typing import Annotated

import questionary
import typer
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
from vox_machina.diarize import diarize_audio
from vox_machina.format import format_transcript_with_speakers
from vox_machina.merge import merge_segments
from vox_machina.rename import (
    extract_quotes,
    extract_speakers,
    parse_speaker_mapping,
    rename_speakers,
)
from vox_machina.summarize import summarize_transcript
from vox_machina.transcribe import convert_to_wav, transcribe_audio


INITIAL_QUOTES = 3
WHISPER_MODELS = ["small", "medium", "large-v3"]

app = typer.Typer(add_completion=False)
console = Console()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """vox: local voice transcription with speaker diarization."""
    print_banner()
    if ctx.invoked_subcommand is None:
        console.print("Run [bold]vox --help[/bold] for usage information.")
        raise typer.Exit(0)


def _require_md(file: Path) -> None:
    if file.suffix.lower() != ".md":
        console.print(f"[red]Error: expected a .md file, got {file.suffix}[/red]")
        raise typer.Exit(1)


def _list_ollama_models() -> list[str]:
    """List locally available Ollama models."""
    try:
        import ollama

        response = ollama.list()
        return [m.model for m in response.models if m.model]
    except Exception:
        return []


def _run_config_questionnaire() -> VoxConfig:
    """Interactive configuration setup."""
    console.print("\n[bold]First-time setup[/bold]\n")

    # Whisper model
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

    # Ollama model
    available = _list_ollama_models()
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


def _ensure_config() -> VoxConfig:
    """Load config, running the questionnaire on first use."""
    if not config_exists():
        return _run_config_questionnaire()
    return load_config()


def _prompt_for_speaker_name(speaker: str, quotes: list[str]) -> str | None:
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


@app.command()
def config() -> None:
    """Configure default models for transcription and summarization."""
    cfg = _run_config_questionnaire()
    console.print(f"\n  Whisper model: [bold]{cfg.whisper_model}[/bold]")
    console.print(f"  Ollama model:  [bold]{cfg.ollama_model}[/bold]")


@app.command()
def transcribe(
    file: Annotated[Path, typer.Argument(help="Audio file to transcribe")],
    output: Annotated[Path | None, typer.Option(help="Output file path")] = None,
    model: Annotated[
        str | None, typer.Option(help="Whisper model size (overrides config)")
    ] = None,
) -> None:
    """Transcribe an audio file with speaker diarization."""
    if not file.exists():
        console.print(f"[red]Error: file not found: {file}[/red]")
        raise typer.Exit(1)

    cfg = _ensure_config()
    whisper_model = model or cfg.whisper_model

    tmp_wav = convert_to_wav(str(file))
    audio_path = tmp_wav or str(file)

    try:
        segments, duration = transcribe_audio(audio_path, model_size=whisper_model)
        speaker_segments = diarize_audio(audio_path)
        merged = merge_segments(segments, speaker_segments)
        markdown = format_transcript_with_speakers(
            merged, source_filename=file.name, duration_seconds=duration
        )

        output_path = output or file.with_suffix(".md")
        output_path.write_text(markdown)
        console.print(f"[green]Transcript saved to {output_path}[/green]")
    finally:
        if tmp_wav:
            Path(tmp_wav).unlink(missing_ok=True)


@app.command()
def rename(
    file: Annotated[Path, typer.Argument(help="Transcript .md file")],
    speakers: Annotated[
        str | None,
        typer.Option(help="Speaker mapping, e.g. 'SPEAKER_00=Niklas,SPEAKER_01=Alex'"),
    ] = None,
    output: Annotated[
        Path | None, typer.Option(help="Output file path (default: overwrite input)")
    ] = None,
) -> None:
    """Replace generic speaker labels with real names."""
    if not file.exists():
        console.print(f"[red]Error: file not found: {file}[/red]")
        raise typer.Exit(1)

    _require_md(file)
    transcript = file.read_text()

    if speakers:
        try:
            mapping = parse_speaker_mapping(speakers)
        except ValueError as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1) from None
    else:
        detected = extract_speakers(transcript)
        if not detected:
            console.print("[yellow]No speaker labels found in transcript.[/yellow]")
            raise typer.Exit(0)

        all_quotes = extract_quotes(transcript, detected)
        mapping = {}
        try:
            for speaker in detected:
                name = _prompt_for_speaker_name(speaker, all_quotes.get(speaker, []))
                if name:
                    mapping[speaker] = name
        except KeyboardInterrupt:
            console.print("\n[yellow]Cancelled.[/yellow]")
            raise typer.Exit(0) from None

    result = rename_speakers(transcript, mapping)
    output_path = output or file
    output_path.write_text(result)
    console.print(f"[green]Speakers renamed in {output_path}[/green]")


@app.command()
def summarize(
    file: Annotated[Path, typer.Argument(help="Transcript .md file to summarize")],
    model: Annotated[
        str | None, typer.Option(help="Ollama model name (overrides config)")
    ] = None,
    prompt: Annotated[
        Path | None, typer.Option(help="Custom prompt template (.md)")
    ] = None,
    output: Annotated[Path | None, typer.Option(help="Output file path")] = None,
) -> None:
    """Summarize a transcript using a local Ollama model."""
    if not file.exists():
        console.print(f"[red]Error: file not found: {file}[/red]")
        raise typer.Exit(1)

    _require_md(file)
    cfg = _ensure_config()
    ollama_model = model or cfg.ollama_model

    transcript = file.read_text()
    prompt_path = str(prompt) if prompt else None
    summary = summarize_transcript(
        transcript, model=ollama_model, prompt_path=prompt_path
    )

    output_path = output or file.with_name(f"{file.stem}-summary.md")
    output_path.write_text(summary)
    console.print(f"[green]Summary saved to {output_path}[/green]")
