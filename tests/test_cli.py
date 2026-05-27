from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from vox_machina.config import VoxConfig
from vox_machina.machina_app import app as machina_app
from vox_machina.vox_app import app as vox_app


runner = CliRunner()
_mock_config = VoxConfig()


# --- vox commands ---


@patch("vox_machina.vox_app.ensure_config", return_value=_mock_config)
@patch("vox_machina.diarize.diarize_audio")
@patch("vox_machina.vox_app.transcribe_audio")
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

    result = runner.invoke(vox_app, ["transcribe", str(audio_file)])

    assert result.exit_code == 0
    output_file = tmp_path / "test.md"
    assert output_file.exists()
    content = output_file.read_text()
    assert "Hello world" in content


@patch("vox_machina.vox_app.ensure_config", return_value=_mock_config)
@patch("vox_machina.diarize.diarize_audio")
@patch("vox_machina.vox_app.transcribe_audio")
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

    result = runner.invoke(vox_app, ["transcribe", str(audio_file)])

    assert result.exit_code == 0
    content = (tmp_path / "meeting.md").read_text()
    assert "SPEAKER_00" in content
    assert "SPEAKER_01" in content


# --- machina commands ---


def test_rename_command_non_interactive(tmp_path: Path) -> None:
    transcript_file = tmp_path / "test.md"
    transcript_file.write_text(
        "# Transcript: test.wav\n\n"
        "**SPEAKER_00** (00:00:01)\nHello\n\n"
        "**SPEAKER_01** (00:00:04)\nHi\n"
    )

    result = runner.invoke(
        machina_app,
        [
            "rename",
            str(transcript_file),
            "--speakers",
            "SPEAKER_00=Alice,SPEAKER_01=Bob",
        ],
    )

    assert result.exit_code == 0
    content = transcript_file.read_text()
    assert "**Alice**" in content
    assert "**Bob**" in content
    assert "SPEAKER_00" not in content


@patch("vox_machina.machina_app.ensure_config", return_value=_mock_config)
@patch("vox_machina.machina_app.summarize_transcript")
def test_summarize_command_creates_summary_file(
    mock_summarize: MagicMock,
    _mock_cfg: MagicMock,
    tmp_path: Path,
) -> None:
    mock_summarize.return_value = "## Summary\nKey topics discussed."

    transcript_file = tmp_path / "meeting.md"
    transcript_file.write_text("# Transcript: meeting.m4a\n\nSome transcript content.")

    result = runner.invoke(machina_app, ["summarize", str(transcript_file)])

    assert result.exit_code == 0
    summary_file = tmp_path / "meeting-summary.md"
    assert summary_file.exists()
    content = summary_file.read_text()
    assert "# Summary: meeting.md" in content
    assert "**Model:** qwen3.5:9b" in content
    assert "**Prompt:** meeting_notes" in content
    assert "Key topics discussed" in content
