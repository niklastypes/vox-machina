from vox_machina.merge import merge_segments
from vox_machina.models import MergedSegment, SpeakerSegment, TranscriptSegment


def test_single_segment_single_speaker() -> None:
    transcripts = [TranscriptSegment(start=0.0, end=2.0, text="Hello")]
    speakers = [SpeakerSegment(start=0.0, end=5.0, speaker="SPEAKER_00")]

    result = merge_segments(transcripts, speakers)

    assert len(result) == 1
    assert result[0] == MergedSegment(
        start=0.0, end=2.0, text="Hello", speaker="SPEAKER_00"
    )


def test_segment_assigned_to_speaker_with_greatest_overlap() -> None:
    transcripts = [TranscriptSegment(start=1.0, end=4.0, text="Overlap test")]
    speakers = [
        SpeakerSegment(start=0.0, end=2.0, speaker="SPEAKER_00"),
        SpeakerSegment(start=2.0, end=5.0, speaker="SPEAKER_01"),
    ]

    result = merge_segments(transcripts, speakers)

    assert len(result) == 1
    assert result[0].speaker == "SPEAKER_01"


def test_multiple_segments_multiple_speakers() -> None:
    transcripts = [
        TranscriptSegment(start=0.0, end=2.0, text="First"),
        TranscriptSegment(start=3.0, end=5.0, text="Second"),
    ]
    speakers = [
        SpeakerSegment(start=0.0, end=2.5, speaker="SPEAKER_00"),
        SpeakerSegment(start=2.5, end=6.0, speaker="SPEAKER_01"),
    ]

    result = merge_segments(transcripts, speakers)

    assert len(result) == 2
    assert result[0].speaker == "SPEAKER_00"
    assert result[1].speaker == "SPEAKER_01"


def test_transcript_with_no_overlapping_speaker_gets_unknown() -> None:
    transcripts = [TranscriptSegment(start=10.0, end=12.0, text="Orphan")]
    speakers = [SpeakerSegment(start=0.0, end=5.0, speaker="SPEAKER_00")]

    result = merge_segments(transcripts, speakers)

    assert len(result) == 1
    assert result[0].speaker == "UNKNOWN"


def test_empty_transcripts_returns_empty() -> None:
    result = merge_segments(
        [], [SpeakerSegment(start=0.0, end=5.0, speaker="SPEAKER_00")]
    )
    assert result == []
