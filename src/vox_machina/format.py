from datetime import date

from vox_machina.models import MergedSegment


def _format_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def _group_consecutive_speakers(
    segments: list[MergedSegment],
) -> list[tuple[str, float, str]]:
    if not segments:
        return []

    groups: list[tuple[str, float, str]] = []
    current_speaker = segments[0].speaker
    current_start = segments[0].start
    current_texts: list[str] = [segments[0].text]

    for seg in segments[1:]:
        if seg.speaker == current_speaker:
            current_texts.append(seg.text)
        else:
            groups.append((current_speaker, current_start, " ".join(current_texts)))
            current_speaker = seg.speaker
            current_start = seg.start
            current_texts = [seg.text]

    groups.append((current_speaker, current_start, " ".join(current_texts)))
    return groups


def format_transcript_with_speakers(
    segments: list[MergedSegment],
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

    grouped = _group_consecutive_speakers(segments)
    for speaker, start, text in grouped:
        lines.append("")
        lines.append(f"**{speaker}** ({_format_time(start)})")
        lines.append(text)

    lines.append("")
    return "\n".join(lines)
