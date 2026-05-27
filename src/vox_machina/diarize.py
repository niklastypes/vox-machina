# ruff: noqa: I001, E402
import contextlib
import logging
import os
import warnings


@contextlib.contextmanager
def _suppress_objc_warnings():
    """Suppress macOS dynamic linker warnings about duplicate AVF classes.

    These warnings are written directly to C-level stderr (fd 2) by the
    Objective-C runtime, bypassing Python's sys.stderr. We need to redirect
    the actual file descriptor to suppress them.
    """
    devnull = os.open(os.devnull, os.O_WRONLY)
    original_fd = os.dup(2)
    os.dup2(devnull, 2)
    os.close(devnull)
    try:
        yield
    finally:
        os.dup2(original_fd, 2)
        os.close(original_fd)


with _suppress_objc_warnings():
    from pyannote.audio import Pipeline

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from vox_machina.models import SpeakerSegment


logger = logging.getLogger(__name__)

DIARIZATION_MODEL = "pyannote/speaker-diarization-community-1"


def diarize_audio(audio_path: str) -> list[SpeakerSegment]:
    """Run speaker diarization on an audio file.

    Returns an empty list if diarization fails (e.g. audio too short),
    which causes the merge step to label everything as UNKNOWN. This is
    the expected fallback for single-speaker recordings.
    """
    console = Console()

    try:
        with (
            _suppress_objc_warnings(),
            Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]Running speaker diarization..."),
            ) as progress,
        ):
            progress.add_task("diarizing", total=None)

            warnings.filterwarnings("ignore", message="std\\(\\): degrees of freedom")
            pipeline = Pipeline.from_pretrained(DIARIZATION_MODEL)
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
