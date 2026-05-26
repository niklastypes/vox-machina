from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from vox_machina.cli import app


runner = CliRunner()


@patch("vox_machina.cli.transcribe_audio")
def test_transcribe_command_creates_md_file(
    mock_transcribe: MagicMock,
    tmp_path: Path,
) -> None:
    from vox_machina.models import TranscriptSegment

    audio_file = tmp_path / "test.wav"
    audio_file.touch()

    mock_transcribe.return_value = (
        [TranscriptSegment(start=0.0, end=2.0, text="Hello world")],
        10.0,
    )

    result = runner.invoke(app, [str(audio_file)])

    assert result.exit_code == 0
    output_file = tmp_path / "test.md"
    assert output_file.exists()
    content = output_file.read_text()
    assert "Hello world" in content
