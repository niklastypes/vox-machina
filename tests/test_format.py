from vox_machina.format import format_transcript
from vox_machina.models import TranscriptSegment


def test_single_segment_formatting() -> None:
    segments = [
        TranscriptSegment(start=1.0, end=3.0, text="Hello world"),
    ]
    result = format_transcript(
        segments, source_filename="meeting.m4a", duration_seconds=180.0
    )

    assert "# Transcript: meeting.m4a" in result
    assert "**Duration:** 00:03:00" in result
    assert "(00:00:01)" in result
    assert "Hello world" in result


def test_multiple_segments() -> None:
    segments = [
        TranscriptSegment(start=0.0, end=1.0, text="Hello"),
        TranscriptSegment(start=1.5, end=3.0, text="World"),
    ]
    result = format_transcript(
        segments, source_filename="test.wav", duration_seconds=3.0
    )

    assert "Hello" in result
    assert "World" in result
    assert result.index("Hello") < result.index("World")


def test_timestamp_formatting() -> None:
    segments = [
        TranscriptSegment(start=3661.0, end=3665.0, text="Late in meeting"),
    ]
    result = format_transcript(
        segments, source_filename="long.m4a", duration_seconds=7200.0
    )

    assert "(01:01:01)" in result
    assert "**Duration:** 02:00:00" in result


def test_empty_segments_produces_header_only() -> None:
    result = format_transcript([], source_filename="empty.wav", duration_seconds=0.0)

    assert "# Transcript: empty.wav" in result
    assert "**Duration:** 00:00:00" in result
