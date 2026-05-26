from vox_machina.format import format_transcript_with_speakers
from vox_machina.models import MergedSegment


def test_single_segment_formatting() -> None:
    segments = [
        MergedSegment(start=1.0, end=3.0, text="Hello world", speaker="SPEAKER_00"),
    ]
    result = format_transcript_with_speakers(
        segments, source_filename="meeting.m4a", duration_seconds=180.0
    )

    assert "# Transcript: meeting.m4a" in result
    assert "**Duration:** 00:03:00" in result
    assert "**SPEAKER_00** (00:00:01)" in result
    assert "Hello world" in result


def test_multiple_segments() -> None:
    segments = [
        MergedSegment(start=0.0, end=1.0, text="Hello", speaker="SPEAKER_00"),
        MergedSegment(start=1.5, end=3.0, text="World", speaker="SPEAKER_01"),
    ]
    result = format_transcript_with_speakers(
        segments, source_filename="test.wav", duration_seconds=3.0
    )

    assert "Hello" in result
    assert "World" in result
    assert result.index("Hello") < result.index("World")


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


def test_consecutive_same_speaker_segments_are_grouped() -> None:
    segments = [
        MergedSegment(start=0.0, end=1.0, text="Hello", speaker="SPEAKER_00"),
        MergedSegment(start=1.0, end=2.0, text="world", speaker="SPEAKER_00"),
    ]
    result = format_transcript_with_speakers(
        segments, source_filename="test.wav", duration_seconds=2.0
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
