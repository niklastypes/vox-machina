from datetime import date

from vox_machina.models import TranscriptSegment


def _format_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def format_transcript(
    segments: list[TranscriptSegment],
    source_filename: str,
    duration_seconds: float,
) -> str:
    lines: list[str] = [
        f"# Transcript: {source_filename}",
        "",
        f"**Date:** {date.today().isoformat()}",
        f"**Duration:** {_format_time(duration_seconds)}",
        "",
        "---",
    ]

    for seg in segments:
        lines.append("")
        lines.append(f"({_format_time(seg.start)})")
        lines.append(seg.text)

    lines.append("")
    return "\n".join(lines)
