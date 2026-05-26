import pytest

from vox_machina.models import TranscriptSegment


def test_transcript_segment_creation() -> None:
    segment = TranscriptSegment(start=0.0, end=1.5, text="Hello world")
    assert segment.start == 0.0
    assert segment.end == 1.5
    assert segment.text == "Hello world"


def test_transcript_segment_rejects_negative_start() -> None:
    with pytest.raises(ValueError):
        TranscriptSegment(start=-1.0, end=1.0, text="bad")


def test_transcript_segment_rejects_end_before_start() -> None:
    with pytest.raises(ValueError):
        TranscriptSegment(start=2.0, end=1.0, text="bad")
