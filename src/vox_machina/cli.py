from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from vox_machina.format import format_transcript
from vox_machina.transcribe import transcribe_audio


app = typer.Typer(add_completion=False)
console = Console()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    file: Annotated[
        Path | None, typer.Argument(help="Audio file to transcribe")
    ] = None,
    output: Annotated[Path | None, typer.Option(help="Output file path")] = None,
    model: Annotated[str, typer.Option(help="Whisper model size")] = "large-v3",
) -> None:
    """vox: local voice transcription with speaker diarization."""
    if ctx.invoked_subcommand is not None:
        return

    if file is None:
        console.print("[red]Error: please provide an audio file to transcribe.[/red]")
        raise typer.Exit(1)

    if not file.exists():
        console.print(f"[red]Error: file not found: {file}[/red]")
        raise typer.Exit(1)

    segments, duration = transcribe_audio(str(file), model_size=model)
    markdown = format_transcript(
        segments, source_filename=file.name, duration_seconds=duration
    )

    output_path = output or file.with_suffix(".md")
    output_path.write_text(markdown)
    console.print(f"[green]Transcript saved to {output_path}[/green]")
