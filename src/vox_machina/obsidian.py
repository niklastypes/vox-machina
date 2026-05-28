"""Generate YAML frontmatter for Obsidian-compatible markdown."""

from datetime import date


def transcript_frontmatter(
    source_filename: str,
    duration: str,
    whisper_model: str = "",
    diarization_model: str = "",
    speakers: list[str] | None = None,
    tags: list[str] | None = None,
) -> str:
    """Generate YAML frontmatter for a transcript."""
    lines = [
        "---",
        "type: transcript",
        f"date: {date.today().isoformat()}",
        f'duration: "{duration}"',
        f"source: {source_filename}",
    ]
    if whisper_model:
        lines.append(f"whisper_model: {whisper_model}")
    if diarization_model:
        lines.append(f"diarization_model: {diarization_model}")
    if speakers:
        lines.append("speakers:")
        for s in speakers:
            lines.append(f"  - {s}")
    _tags = tags or ["transcript"]
    lines.append("tags:")
    for t in _tags:
        lines.append(f"  - {t}")
    lines.append("---")
    return "\n".join(lines)


def summary_frontmatter(
    source_filename: str,
    model: str,
    prompt_name: str,
    whisper_model: str = "",
    diarization_model: str = "",
    tags: list[str] | None = None,
) -> str:
    """Generate YAML frontmatter for a summary."""
    lines = [
        "---",
        "type: summary",
        f"date: {date.today().isoformat()}",
        f"source: {source_filename}",
        f"model: {model}",
        f"prompt: {prompt_name}",
    ]
    if whisper_model:
        lines.append(f"whisper_model: {whisper_model}")
    if diarization_model:
        lines.append(f"diarization_model: {diarization_model}")
    _tags = tags or ["summary", prompt_name.replace("_", "-")]
    lines.append("tags:")
    for t in _tags:
        lines.append(f"  - {t}")
    lines.append("---")
    return "\n".join(lines)
