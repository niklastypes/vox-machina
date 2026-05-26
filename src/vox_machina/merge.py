from vox_machina.models import MergedSegment, SpeakerSegment, TranscriptSegment


def _overlap(t_start: float, t_end: float, s_start: float, s_end: float) -> float:
    overlap_start = max(t_start, s_start)
    overlap_end = min(t_end, s_end)
    return max(0.0, overlap_end - overlap_start)


def merge_segments(
    transcripts: list[TranscriptSegment],
    speakers: list[SpeakerSegment],
) -> list[MergedSegment]:
    merged: list[MergedSegment] = []
    for t in transcripts:
        best_speaker = "UNKNOWN"
        best_overlap = 0.0
        for s in speakers:
            ov = _overlap(t.start, t.end, s.start, s.end)
            if ov > best_overlap:
                best_overlap = ov
                best_speaker = s.speaker
        merged.append(
            MergedSegment(start=t.start, end=t.end, text=t.text, speaker=best_speaker)
        )
    return merged
