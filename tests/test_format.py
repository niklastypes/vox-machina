from vox_machina.format import format_transcript_with_speakers
from vox_machina.models import MergedSegment


# --- Single speaker: per-segment timestamps, no speaker labels ---


def test_single_speaker_uses_per_segment_timestamps() -> None:
    segments = [
        MergedSegment(start=0.0, end=1.0, text="Hello", speaker="SPEAKER_00"),
        MergedSegment(start=1.5, end=3.0, text="World", speaker="SPEAKER_00"),
    ]
    result = format_transcript_with_speakers(
        segments, source_filename="test.wav", duration_seconds=3.0
    )

    assert "(00:00:00)" in result
    assert "(00:00:01)" in result
    assert "SPEAKER_00" not in result


def test_unknown_speaker_uses_per_segment_timestamps() -> None:
    segments = [
        MergedSegment(start=0.0, end=1.0, text="Hello", speaker="UNKNOWN"),
        MergedSegment(start=2.0, end=3.0, text="World", speaker="UNKNOWN"),
    ]
    result = format_transcript_with_speakers(
        segments, source_filename="test.wav", duration_seconds=3.0
    )

    assert "(00:00:00)" in result
    assert "(00:00:02)" in result
    assert "UNKNOWN" not in result


# --- Multi speaker: speaker labels with grouping ---


def test_multi_speaker_formatting() -> None:
    segments = [
        MergedSegment(start=1.0, end=3.0, text="Hello world", speaker="SPEAKER_00"),
        MergedSegment(start=3.0, end=5.0, text="Hi there", speaker="SPEAKER_01"),
    ]
    result = format_transcript_with_speakers(
        segments, source_filename="meeting.m4a", duration_seconds=180.0
    )

    assert "# Transcript: meeting.m4a" in result
    assert "**Duration:** 00:03:00" in result
    assert "**SPEAKER_00** (00:00:01)" in result
    assert "**SPEAKER_01** (00:00:03)" in result


def test_consecutive_same_speaker_segments_are_grouped() -> None:
    segments = [
        MergedSegment(start=0.0, end=1.0, text="Hello", speaker="SPEAKER_00"),
        MergedSegment(start=1.0, end=2.0, text="world", speaker="SPEAKER_00"),
        MergedSegment(start=2.0, end=3.0, text="Hi", speaker="SPEAKER_01"),
    ]
    result = format_transcript_with_speakers(
        segments, source_filename="test.wav", duration_seconds=3.0
    )

    assert result.count("**SPEAKER_00**") == 1
    assert "Hello world" in result


def test_different_speakers_get_separate_blocks() -> None:
    segments = [
        MergedSegment(start=0.0, end=1.0, text="Hello", speaker="SPEAKER_00"),
        MergedSegment(start=1.0, end=2.0, text="Hi there", speaker="SPEAKER_01"),
    ]
    result = format_transcript_with_speakers(
        segments, source_filename="test.wav", duration_seconds=2.0
    )

    assert "**SPEAKER_00**" in result
    assert "**SPEAKER_01**" in result
    assert result.index("SPEAKER_00") < result.index("SPEAKER_01")


# --- Shared behavior ---


def test_timestamp_formatting() -> None:
    segments = [
        MergedSegment(
            start=3661.0, end=3665.0, text="Late in meeting", speaker="SPEAKER_00"
        ),
    ]
    result = format_transcript_with_speakers(
        segments, source_filename="long.m4a", duration_seconds=7200.0
    )

    assert "(01:01:01)" in result
    assert "**Duration:** 02:00:00" in result


def test_empty_segments_produces_header_only() -> None:
    result = format_transcript_with_speakers(
        [], source_filename="empty.wav", duration_seconds=0.0
    )

    assert "# Transcript: empty.wav" in result
    assert "**Duration:** 00:00:00" in result


def test_whisper_model_included_in_header() -> None:
    result = format_transcript_with_speakers(
        [], source_filename="test.wav", duration_seconds=0.0, whisper_model="small"
    )

    assert "**Whisper model:** small" in result


def test_whisper_model_omitted_when_empty() -> None:
    result = format_transcript_with_speakers(
        [], source_filename="test.wav", duration_seconds=0.0
    )

    assert "Whisper model" not in result
