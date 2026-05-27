from pathlib import Path
from typing import Annotated

import questionary
import typer
from rich.console import Console

from vox_machina.diarize import diarize_audio
from vox_machina.format import format_transcript_with_speakers
from vox_machina.merge import merge_segments
from vox_machina.rename import (
    extract_quotes,
    extract_speakers,
    parse_speaker_mapping,
    rename_speakers,
)
from vox_machina.transcribe import convert_to_wav, transcribe_audio


INITIAL_QUOTES = 3

app = typer.Typer(add_completion=False)
console = Console()


def _require_md(file: Path) -> None:
    if file.suffix.lower() != ".md":
        console.print(f"[red]Error: expected a .md file, got {file.suffix}[/red]")
        raise typer.Exit(1)


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
def transcribe(
    file: Annotated[Path, typer.Argument(help="Audio file to transcribe")],
    output: Annotated[Path | None, typer.Option(help="Output file path")] = None,
    model: Annotated[str, typer.Option(help="Whisper model size")] = "large-v3",
) -> None:
    """Transcribe an audio file with speaker diarization."""
    if not file.exists():
        console.print(f"[red]Error: file not found: {file}[/red]")
        raise typer.Exit(1)

    tmp_wav = convert_to_wav(str(file))
    audio_path = tmp_wav or str(file)

    try:
        segments, duration = transcribe_audio(audio_path, model_size=model)
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
