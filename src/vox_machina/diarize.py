import logging

from pyannote.audio import Pipeline
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from vox_machina.models import SpeakerSegment


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
