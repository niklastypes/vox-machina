# ruff: noqa: I001, E402
import io
import logging
import sys
import warnings

# Suppress objc duplicate class warnings emitted by pyannote's bundled av
# library conflicting with system ffmpeg. These are harmless stderr noise
# from the macOS dynamic linker, not Python warnings.
_original_stderr = sys.stderr
sys.stderr = io.StringIO()

from pyannote.audio import Pipeline  # noqa: E402

_captured = sys.stderr.getvalue()
sys.stderr = _original_stderr
for line in _captured.splitlines():
    if "objc[" not in line:
        print(line, file=sys.stderr)  # noqa: T201

from rich.console import Console  # noqa: E402
from rich.progress import Progress, SpinnerColumn, TextColumn  # noqa: E402

from vox_machina.models import SpeakerSegment  # noqa: E402


logger = logging.getLogger(__name__)


def diarize_audio(audio_path: str) -> list[SpeakerSegment]:
    """Run speaker diarization on an audio file.

    Returns an empty list if diarization fails (e.g. audio too short),
    which causes the merge step to label everything as UNKNOWN. This is
    the expected fallback for single-speaker recordings.
    """
    console = Console()

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Running speaker diarization..."),
        ) as progress:
            progress.add_task("diarizing", total=None)

            warnings.filterwarnings("ignore", message="std\\(\\): degrees of freedom")
            pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-community-1",
            )
            if pipeline is None:
                msg = "Failed to load pyannote pipeline"
                raise RuntimeError(msg)
            result = pipeline(audio_path)
            annotation = result.speaker_diarization

            segments: list[SpeakerSegment] = []
            for turn, _, speaker in annotation.itertracks(yield_label=True):
                segments.append(
                    SpeakerSegment(
                        start=turn.start,
                        end=turn.end,
                        speaker=speaker,
                    )
                )

        return segments

    except Exception:
        logger.exception("Diarization failed, falling back to no speaker labels")
        console.print(
            "[yellow]Warning: diarization failed (audio may be too short). "
            "Proceeding without speaker labels.[/yellow]"
        )
        return []
