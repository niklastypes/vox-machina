import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from faster_whisper import WhisperModel
from rich.progress import Progress, SpinnerColumn, TextColumn

from vox_machina.models import TranscriptSegment


def convert_to_wav(audio_path: str) -> str | None:
    """Convert audio to 16kHz mono wav using system ffmpeg.

    Returns path to temp wav file, or None if the input is already wav.
    Caller is responsible for cleaning up the temp file.
    """
    if Path(audio_path).suffix.lower() == ".wav":
        return None

    if not shutil.which("ffmpeg"):
        msg = (
            "ffmpeg is required for non-wav audio formats. "
            "Install it with: brew install ffmpeg"
        )
        raise RuntimeError(msg)

    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".wav")

    os.close(tmp_fd)

    subprocess.run(
        [
            "ffmpeg",
            "-i",
            audio_path,
            "-ar",
            "16000",
            "-ac",
            "1",
            tmp_path,
            "-y",
        ],
        capture_output=True,
        check=True,
    )
    return tmp_path


def transcribe_audio(
    audio_path: str,
    model_size: str = "large-v3",
) -> tuple[list[TranscriptSegment], float]:
    """Transcribe audio file and return segments with total duration."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]Loading whisper model..."),
    ) as progress:
        progress.add_task("loading", total=None)
        model = WhisperModel(model_size, device="cpu", compute_type="int8")

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]Transcribing audio..."),
    ) as progress:
        progress.add_task("transcribing", total=None)
        raw_segments, info = model.transcribe(audio_path, beam_size=5)
        segments = [
            TranscriptSegment(start=seg.start, end=seg.end, text=seg.text.strip())
            for seg in raw_segments
        ]

    return segments, info.duration
