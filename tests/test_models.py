import pytest

from vox_machina.models import MergedSegment, SpeakerSegment, TranscriptSegment


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


def test_speaker_segment_creation() -> None:
    segment = SpeakerSegment(start=0.0, end=5.0, speaker="SPEAKER_00")
    assert segment.speaker == "SPEAKER_00"


def test_merged_segment_creation() -> None:
    segment = MergedSegment(start=0.0, end=1.5, text="Hello", speaker="SPEAKER_00")
    assert segment.text == "Hello"
    assert segment.speaker == "SPEAKER_00"
