from datetime import date

from vox_machina.models import MergedSegment
from vox_machina.obsidian import transcript_frontmatter


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


def _is_multi_speaker(segments: list[MergedSegment]) -> bool:
    speakers = {seg.speaker for seg in segments}
    speakers.discard("UNKNOWN")
    return len(speakers) > 1


def format_transcript_with_speakers(
    segments: list[MergedSegment],
    source_filename: str,
    duration_seconds: float,
    whisper_model: str = "",
    diarization_model: str = "",
    timestamps: bool = True,
    obsidian_mode: bool = False,
) -> str:
    duration_str = _format_time(duration_seconds)

    if obsidian_mode:
        speakers = sorted({seg.speaker for seg in segments} - {"UNKNOWN"})
        frontmatter = transcript_frontmatter(
            source_filename=source_filename,
            duration=duration_str,
            whisper_model=whisper_model,
            diarization_model=diarization_model,
            speakers=speakers or None,
        )
        lines: list[str] = [
            frontmatter,
            "",
            f"# Transcript: {source_filename}",
            "",
        ]
    else:
        lines = [
            f"# Transcript: {source_filename}",
            "",
            f"**Date:** {date.today().isoformat()}",
            f"**Duration:** {duration_str}",
        ]
        if whisper_model:
            lines.append(f"**Whisper model:** {whisper_model}")
        if diarization_model:
            lines.append(f"**Diarization model:** {diarization_model}")
        lines.extend(["", "---"])

    if _is_multi_speaker(segments):
        grouped = _group_consecutive_speakers(segments)
        for speaker, start, text in grouped:
            lines.append("")
            if timestamps:
                lines.append(f"**{speaker}** ({_format_time(start)})")
            else:
                lines.append(f"**{speaker}**")
            lines.append(text)
    else:
        for seg in segments:
            lines.append("")
            if timestamps:
                lines.append(f"({_format_time(seg.start)})")
            lines.append(seg.text)

    lines.append("")
    return "\n".join(lines)
