from faster_whisper import WhisperModel
from rich.progress import Progress, SpinnerColumn, TextColumn

from vox_machina.models import TranscriptSegment


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
