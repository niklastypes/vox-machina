"""vox CLI: audio transcription with speaker diarization."""

import sys
from pathlib import Path
from typing import Annotated

import typer

from vox_machina.banner import print_banner
from vox_machina.cli import (
    config_command,
    console,
    ensure_config,
)
from vox_machina.format import format_transcript_with_speakers
from vox_machina.merge import merge_segments
from vox_machina.transcribe import convert_to_wav, transcribe_audio


app = typer.Typer(add_completion=False)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """vox: voice transcription with speaker diarization."""
    if ctx.invoked_subcommand is None:
        console.print("Run [bold]vox --help[/bold] for usage information.")
        raise typer.Exit(0)


@app.command()
def transcribe(
    file: Annotated[Path, typer.Argument(help="Audio file to transcribe")],
    output: Annotated[Path | None, typer.Option(help="Output file path")] = None,
    model: Annotated[
        str | None, typer.Option(help="Whisper model size (overrides config)")
    ] = None,
    language: Annotated[
        str | None,
        typer.Option(help="Language code, e.g. 'de', 'en' (auto-detect if omitted)"),
    ] = None,
    no_timestamps: Annotated[
        bool, typer.Option("--no-timestamps", help="Omit timestamps from transcript")
    ] = False,
) -> None:
    """Transcribe an audio file with speaker diarization."""
    if not file.exists():
        console.print(f"[red]Error: file not found: {file}[/red]")
        raise typer.Exit(1)

    cfg = ensure_config()
    whisper_model = model or cfg.whisper_model

    tmp_wav = convert_to_wav(str(file))
    audio_path = tmp_wav or str(file)

    try:
        segments, duration = transcribe_audio(
            audio_path, model_size=whisper_model, language=language
        )
        from vox_machina.diarize import DIARIZATION_MODEL, diarize_audio

        speaker_segments = diarize_audio(audio_path)
        merged = merge_segments(segments, speaker_segments)
        markdown = format_transcript_with_speakers(
            merged,
            source_filename=file.name,
            duration_seconds=duration,
            whisper_model=whisper_model,
            diarization_model=DIARIZATION_MODEL,
            timestamps=not no_timestamps,
        )

        output_path = output or file.with_suffix(".md")
        output_path.write_text(markdown)
        console.print(f"[green]Transcript saved to {output_path}[/green]")
    finally:
        if tmp_wav:
            Path(tmp_wav).unlink(missing_ok=True)


@app.command()
def config() -> None:
    """Configure default models for transcription and summarization."""
    config_command()


@app.command()
def prepare() -> None:
    """Download all required models (whisper, diarization, ollama)."""
    from vox_machina.prepare import prepare_all

    cfg = ensure_config()
    prepare_all(cfg)


def main_with_banner() -> None:
    """Entry point that prints the banner before running the app."""
    print_banner()
    app(sys.argv[1:])
