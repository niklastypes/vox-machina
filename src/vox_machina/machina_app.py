"""machina CLI: AI-powered text processing for transcripts."""

from datetime import date
from pathlib import Path
from typing import Annotated

import typer

from vox_machina.cli import (
    banner_callback,
    config_command,
    console,
    ensure_config,
    prompt_for_speaker_name,
    require_md,
)
from vox_machina.label import (
    extract_quotes,
    extract_speakers,
    label_speakers,
    parse_speaker_mapping,
)
from vox_machina.summarize import summarize_transcript


app = typer.Typer(add_completion=False)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """machina: AI-powered summarization and text processing."""
    banner_callback(ctx, "machina")


@app.command()
def label(
    file: Annotated[Path, typer.Argument(help="Transcript .md file")],
    speakers: Annotated[
        str | None,
        typer.Option(help="Speaker mapping, e.g. 'SPEAKER_00=Alice,SPEAKER_01=Bob'"),
    ] = None,
    output: Annotated[Path | None, typer.Option(help="Output file path")] = None,
) -> None:
    """Replace generic speaker labels with real names."""
    if not file.exists():
        console.print(f"[red]Error: file not found: {file}[/red]")
        raise typer.Exit(1)

    require_md(file)
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
                name = prompt_for_speaker_name(speaker, all_quotes.get(speaker, []))
                if name:
                    mapping[speaker] = name
        except KeyboardInterrupt:
            console.print("\n[yellow]Cancelled.[/yellow]")
            raise typer.Exit(0) from None

    result = label_speakers(transcript, mapping)
    output_path = output or file.with_stem(f"{file.stem}_labeled")
    output_path.write_text(result)
    console.print(f"[green]Speakers labeled in {output_path}[/green]")


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

    require_md(file)
    cfg = ensure_config()
    ollama_model = model or cfg.ollama_model

    transcript = file.read_text()
    prompt_name = prompt.stem if prompt else "meeting_notes"
    prompt_path = str(prompt) if prompt else None
    summary = summarize_transcript(
        transcript, model=ollama_model, prompt_path=prompt_path
    )

    header = (
        f"# Summary: {file.name}\n"
        f"\n"
        f"**Date:** {date.today().isoformat()}\n"
        f"**Model:** {ollama_model}\n"
        f"**Prompt:** {prompt_name}\n"
        f"\n"
        f"---\n"
        f"\n"
    )

    output_path = output or file.with_stem(f"{file.stem}_summarized")
    output_path.write_text(header + summary)
    console.print(f"[green]Summary saved to {output_path}[/green]")


@app.command()
def config() -> None:
    """Configure default models for transcription and summarization."""
    config_command()
