from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from vox_machina.cli import app
from vox_machina.config import VoxConfig


runner = CliRunner()
_mock_config = VoxConfig()


@patch("vox_machina.cli._ensure_config", return_value=_mock_config)
@patch("vox_machina.cli.diarize_audio")
@patch("vox_machina.cli.transcribe_audio")
def test_transcribe_command_creates_md_file(
    mock_transcribe: MagicMock,
    mock_diarize: MagicMock,
    _mock_cfg: MagicMock,
    tmp_path: Path,
) -> None:
    from vox_machina.models import TranscriptSegment

    audio_file = tmp_path / "test.wav"
    audio_file.touch()

    mock_transcribe.return_value = (
        [TranscriptSegment(start=0.0, end=2.0, text="Hello world")],
        10.0,
    )
    mock_diarize.return_value = []

    result = runner.invoke(app, ["transcribe", str(audio_file)])

    assert result.exit_code == 0
    output_file = tmp_path / "test.md"
    assert output_file.exists()
    content = output_file.read_text()
    assert "Hello world" in content


@patch("vox_machina.cli._ensure_config", return_value=_mock_config)
@patch("vox_machina.cli.diarize_audio")
@patch("vox_machina.cli.transcribe_audio")
def test_transcribe_command_with_diarization(
    mock_transcribe: MagicMock,
    mock_diarize: MagicMock,
    _mock_cfg: MagicMock,
    tmp_path: Path,
) -> None:
    from vox_machina.models import SpeakerSegment, TranscriptSegment

    audio_file = tmp_path / "meeting.wav"
    audio_file.touch()

    mock_transcribe.return_value = (
        [
            TranscriptSegment(start=0.0, end=2.0, text="Hello"),
            TranscriptSegment(start=2.0, end=4.0, text="Hi there"),
        ],
        10.0,
    )
    mock_diarize.return_value = [
        SpeakerSegment(start=0.0, end=2.5, speaker="SPEAKER_00"),
        SpeakerSegment(start=2.5, end=5.0, speaker="SPEAKER_01"),
    ]

    result = runner.invoke(app, ["transcribe", str(audio_file)])

    assert result.exit_code == 0
    content = (tmp_path / "meeting.md").read_text()
    assert "SPEAKER_00" in content
    assert "SPEAKER_01" in content


def test_rename_command_non_interactive(tmp_path: Path) -> None:
    transcript_file = tmp_path / "test.md"
    transcript_file.write_text(
        "# Transcript: test.wav\n\n"
        "**SPEAKER_00** (00:00:01)\nHello\n\n"
        "**SPEAKER_01** (00:00:04)\nHi\n"
    )

    result = runner.invoke(
        app,
        [
            "rename",
            str(transcript_file),
            "--speakers",
            "SPEAKER_00=Niklas,SPEAKER_01=Alex",
        ],
    )

    assert result.exit_code == 0
    content = transcript_file.read_text()
    assert "**Niklas**" in content
    assert "**Alex**" in content
    assert "SPEAKER_00" not in content


@patch("vox_machina.cli._ensure_config", return_value=_mock_config)
@patch("vox_machina.cli.summarize_transcript")
def test_summarize_command_creates_summary_file(
    mock_summarize: MagicMock,
    _mock_cfg: MagicMock,
    tmp_path: Path,
) -> None:
    mock_summarize.return_value = "## Summary\nKey topics discussed."

    transcript_file = tmp_path / "meeting.md"
    transcript_file.write_text("# Transcript: meeting.m4a\n\nSome transcript content.")

    result = runner.invoke(app, ["summarize", str(transcript_file)])

    assert result.exit_code == 0
    summary_file = tmp_path / "meeting-summary.md"
    assert summary_file.exists()
    assert "Key topics discussed" in summary_file.read_text()
