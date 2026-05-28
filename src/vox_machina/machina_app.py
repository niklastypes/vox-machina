"""machina CLI: AI-powered text processing for transcripts."""

import sys
from datetime import date
from pathlib import Path
from typing import Annotated

import questionary
import typer

from vox_machina.banner import print_banner
from vox_machina.cli import (
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
from vox_machina.summarize import (
    PROMPT_DESCRIPTIONS,
    list_builtin_prompts,
    summarize_transcript,
)


app = typer.Typer(add_completion=False)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """machina: AI-powered summarization and text processing."""
    if ctx.invoked_subcommand is None:
        console.print("Run [bold]machina --help[/bold] for usage information.")
        raise typer.Exit(0)


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
        str | None,
        typer.Option(
            help="Prompt template ("
            + ", ".join(
                f"{p}: {PROMPT_DESCRIPTIONS.get(p, '')}" for p in list_builtin_prompts()
            )
            + ") or a file path"
        ),
    ] = None,
    detail: Annotated[
        str, typer.Option(help="Level of detail: 'concise' or 'detailed'")
    ] = "concise",
    output: Annotated[Path | None, typer.Option(help="Output file path")] = None,
) -> None:
    """Summarize a transcript using a local Ollama model."""
    if not file.exists():
        console.print(f"[red]Error: file not found: {file}[/red]")
        raise typer.Exit(1)

    require_md(file)
    cfg = ensure_config()
    ollama_model = model or cfg.ollama_model

    if prompt is None:
        available = list_builtin_prompts()
        prompt_name = questionary.select(
            "Prompt template:",
            choices=[
                questionary.Choice(
                    f"{p} - {PROMPT_DESCRIPTIONS.get(p, '')}",
                    value=p,
                )
                for p in available
            ],
            default="meeting_notes",
        ).ask()
        if prompt_name is None:
            raise typer.Exit(0)
    else:
        prompt_name = prompt

    transcript = file.read_text()
    summary = summarize_transcript(
        transcript, model=ollama_model, prompt_name=prompt_name, detail=detail
    )

    if cfg.obsidian_mode:
        from vox_machina.diarize import DIARIZATION_MODEL
        from vox_machina.obsidian import summary_frontmatter

        header = (
            summary_frontmatter(
                source_filename=file.name,
                model=ollama_model,
                prompt_name=prompt_name,
                whisper_model=cfg.whisper_model,
                diarization_model=DIARIZATION_MODEL,
            )
            + f"\n\n# Summary: {file.name}\n\n"
        )
    else:
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


def main_with_banner() -> None:
    """Entry point that prints the banner before running the app."""
    print_banner()
    app(sys.argv[1:])
