from pathlib import Path
from typing import Annotated

import questionary
import typer
from rich.console import Console

from vox_machina.diarize import diarize_audio
from vox_machina.format import format_transcript_with_speakers
from vox_machina.merge import merge_segments
from vox_machina.rename import (
    extract_first_quotes,
    extract_speakers,
    parse_speaker_mapping,
    rename_speakers,
)
from vox_machina.transcribe import convert_to_wav, transcribe_audio


app = typer.Typer(add_completion=False)
console = Console()


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

    transcript = file.read_text()

    if speakers:
        mapping = parse_speaker_mapping(speakers)
    else:
        detected = extract_speakers(transcript)
        if not detected:
            console.print("[yellow]No speaker labels found in transcript.[/yellow]")
            raise typer.Exit(0)

        first_quotes = extract_first_quotes(transcript, detected)
        mapping = {}
        for speaker in detected:
            quote = first_quotes.get(speaker, "(no quote found)")
            name = questionary.text(
                f'{speaker} said: "{quote}"\nWho is this?',
            ).ask()
            if name:
                mapping[speaker] = name

    result = rename_speakers(transcript, mapping)
    output_path = output or file
    output_path.write_text(result)
    console.print(f"[green]Speakers renamed in {output_path}[/green]")
