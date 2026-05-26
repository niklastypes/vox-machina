# vox-machina Roadmap

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

Each slice is independently useful and ends with passing tests, lint, and a commit.

| Slice | Version | What it delivers |
|-------|---------|-----------------|
| Skateboard | v0.1.0 | `vox file.m4a` produces timestamped transcript |
| Scooter | v0.2.0 | Adds speaker diarization (SPEAKER_00, SPEAKER_01, ...) |
| Bicycle | v0.3.0 | `vox rename` for interactive speaker label replacement |
| Motorcycle | v0.4.0 | `vox summarize` via local Ollama with prompt templates |
| Polish | v0.5.0 | ASCII banner, polished rich UX throughout |
| Summaries+ | v0.6.0 | Multiple prompt templates + chunked summarization for long recordings |
| Obsidian | v0.7.0 | Obsidian-ready output with frontmatter, tags, wikilinks |

---

## v0.1.0: Transcription (Skateboard)

**Goal:** `vox meeting.m4a` produces a timestamped transcript as markdown. Already useful for personal voice memos.

**Note:** Project already scaffolded from kindling. Dependencies are added alongside the code that needs them.

---

### Task 1.1: Data Models

**Files:**
- Create: `src/vox_machina/models.py`
- Create: `tests/test_models.py`
- Modify: `pyproject.toml` (add pydantic)

- [ ] **Step 1: Add pydantic dependency**

Add to `[project.dependencies]` in `pyproject.toml`:

```toml
"pydantic>=2.0.0",
```

Then sync:

```bash
uv sync
```

- [ ] **Step 2: Write failing tests for data models**

`tests/test_models.py`:

```python
import pytest

from vox_machina.models import TranscriptSegment


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
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
uv run pytest tests/test_models.py -v
```

Expected: FAIL (cannot import `vox_machina.models`)

- [ ] **Step 4: Implement models**

`src/vox_machina/models.py`:

```python
from pydantic import BaseModel, model_validator


class TranscriptSegment(BaseModel):
    start: float
    end: float
    text: str

    @model_validator(mode="after")
    def validate_times(self) -> "TranscriptSegment":
        if self.start < 0:
            raise ValueError("start must be non-negative")
        if self.end < self.start:
            raise ValueError("end must be >= start")
        return self
```

Note: `SpeakerSegment` and `MergedSegment` are added in v0.2.0 when diarization lands.

- [ ] **Step 5: Run tests to verify they pass**

```bash
uv run pytest tests/test_models.py -v
```

Expected: all 3 PASS

- [ ] **Step 6: Commit**

```bash
git add src/vox_machina/models.py tests/test_models.py pyproject.toml uv.lock
git commit -m "feat: add TranscriptSegment pydantic model"
```

---

### Task 1.2: Markdown Formatting (No Speakers)

**Files:**
- Create: `src/vox_machina/format.py`
- Create: `tests/test_format.py`

- [ ] **Step 1: Write failing tests**

`tests/test_format.py`:

```python
from vox_machina.format import format_transcript
from vox_machina.models import TranscriptSegment


def test_single_segment_formatting() -> None:
    segments = [
        TranscriptSegment(start=1.0, end=3.0, text="Hello world"),
    ]
    result = format_transcript(
        segments, source_filename="meeting.m4a", duration_seconds=180.0
    )

    assert "# Transcript: meeting.m4a" in result
    assert "**Duration:** 00:03:00" in result
    assert "(00:00:01)" in result
    assert "Hello world" in result


def test_multiple_segments() -> None:
    segments = [
        TranscriptSegment(start=0.0, end=1.0, text="Hello"),
        TranscriptSegment(start=1.5, end=3.0, text="World"),
    ]
    result = format_transcript(segments, source_filename="test.wav", duration_seconds=3.0)

    assert "Hello" in result
    assert "World" in result
    assert result.index("Hello") < result.index("World")


def test_timestamp_formatting() -> None:
    segments = [
        TranscriptSegment(start=3661.0, end=3665.0, text="Late in meeting"),
    ]
    result = format_transcript(segments, source_filename="long.m4a", duration_seconds=7200.0)

    assert "(01:01:01)" in result
    assert "**Duration:** 02:00:00" in result


def test_empty_segments_produces_header_only() -> None:
    result = format_transcript([], source_filename="empty.wav", duration_seconds=0.0)

    assert "# Transcript: empty.wav" in result
    assert "**Duration:** 00:00:00" in result
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_format.py -v
```

Expected: FAIL (cannot import `vox_machina.format`)

- [ ] **Step 3: Implement formatter**

`src/vox_machina/format.py`:

```python
from datetime import date

from vox_machina.models import TranscriptSegment


def _format_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def format_transcript(
    segments: list[TranscriptSegment],
    source_filename: str,
    duration_seconds: float,
) -> str:
    lines: list[str] = [
        f"# Transcript: {source_filename}",
        "",
        f"**Date:** {date.today().isoformat()}",
        f"**Duration:** {_format_time(duration_seconds)}",
        "",
        "---",
    ]

    for seg in segments:
        lines.append("")
        lines.append(f"({_format_time(seg.start)})")
        lines.append(seg.text)

    lines.append("")
    return "\n".join(lines)
```

Note: This formatter is simple for v0.1.0 (no speaker grouping). It gets replaced in v0.2.0 by `format_transcript_with_speakers()`.

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_format.py -v
```

Expected: all 4 PASS

- [ ] **Step 5: Commit**

```bash
git add src/vox_machina/format.py tests/test_format.py
git commit -m "feat: add markdown transcript formatter with timestamps"
```

---

### Task 1.3: Transcription Module

**Files:**
- Create: `src/vox_machina/transcribe.py`
- Modify: `pyproject.toml` (add faster-whisper, rich)

This wraps faster-whisper. Depends on ML models, so tested via integration (end of slice).

- [ ] **Step 1: Add faster-whisper and rich dependencies**

Add to `[project.dependencies]` in `pyproject.toml`:

```toml
"faster-whisper>=1.1.0",
"rich>=13.0.0",
```

Then sync:

```bash
uv sync
```

- [ ] **Step 2: Implement transcription module**

`src/vox_machina/transcribe.py`:

```python
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
```

- [ ] **Step 3: Verify import works**

```bash
uv run python -c "from vox_machina.transcribe import transcribe_audio; print('OK')"
```

Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add src/vox_machina/transcribe.py pyproject.toml uv.lock
git commit -m "feat: add faster-whisper transcription module"
```

---

### Task 1.4: CLI (Transcribe Only)

**Files:**
- Create: `src/vox_machina/cli.py`
- Create: `tests/test_cli.py`
- Modify: `pyproject.toml` (add typer, CLI entry point)

- [ ] **Step 1: Add typer dependency and CLI entry point**

Add to `[project.dependencies]` in `pyproject.toml`:

```toml
"typer>=0.15.0",
```

Add CLI entry point:

```toml
[project.scripts]
vox = "vox_machina.cli:app"
```

Then sync:

```bash
uv sync
```

- [ ] **Step 2: Write failing test for transcribe command**

`tests/test_cli.py`:

```python
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
```

- [ ] **Step 3: Run test to verify it fails**

```bash
uv run pytest tests/test_cli.py -v
```

Expected: FAIL (cannot import `vox_machina.cli`)

- [ ] **Step 4: Implement CLI (transcribe only)**

`src/vox_machina/cli.py`:

```python
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console

from vox_machina.format import format_transcript
from vox_machina.transcribe import transcribe_audio

app = typer.Typer(add_completion=False)
console = Console()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    file: Annotated[Optional[Path], typer.Argument(help="Audio file to transcribe")] = None,
    output: Annotated[Optional[Path], typer.Option(help="Output file path")] = None,
    model: Annotated[str, typer.Option(help="Whisper model size")] = "large-v3",
) -> None:
    """vox: local voice transcription with speaker diarization."""
    if ctx.invoked_subcommand is not None:
        return

    if file is None:
        console.print("[red]Error: please provide an audio file to transcribe.[/red]")
        raise typer.Exit(1)

    if not file.exists():
        console.print(f"[red]Error: file not found: {file}[/red]")
        raise typer.Exit(1)

    segments, duration = transcribe_audio(str(file), model_size=model)
    markdown = format_transcript(segments, source_filename=file.name, duration_seconds=duration)

    output_path = output or file.with_suffix(".md")
    output_path.write_text(markdown)
    console.print(f"[green]Transcript saved to {output_path}[/green]")
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
uv run pytest tests/test_cli.py -v
```

Expected: PASS

- [ ] **Step 6: Run full test suite + lint**

```bash
uv run pytest -v
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
```

Expected: all pass. Fix formatting issues with `uv run ruff format src/ tests/` if needed.

- [ ] **Step 7: Commit**

```bash
git add src/vox_machina/cli.py tests/test_cli.py pyproject.toml uv.lock
git commit -m "feat: add CLI with transcribe command"
```

- [ ] **Step 8: Smoke test (manual)**

Find or record a short audio file (~30 seconds).

```bash
uv run vox test_audio.m4a
```

Expected: `test_audio.md` appears with timestamped transcript (no speaker labels yet).

---

## v0.2.0: Speaker Diarization (Scooter)

**Goal:** `vox meeting.m4a` now produces a transcript with `SPEAKER_00`, `SPEAKER_01`, etc. labels. Useful for meetings.

**Prerequisite:** v0.1.0 complete

**Breaking change:** Output format changes from v0.1.0. Timestamps that were bare `(00:00:01)` now include a speaker label: `**SPEAKER_00** (00:00:01)`. This is expected as part of the skateboard-to-scooter progression. The v0.1.0 `format_transcript()` is replaced by `format_transcript_with_speakers()` (no external consumers yet, so no need to preserve the old function).

---

### Task 2.1: Add Diarization Models

**Files:**
- Modify: `src/vox_machina/models.py`
- Modify: `tests/test_models.py`

- [ ] **Step 1: Add failing tests for new models**

Append to `tests/test_models.py`:

```python
from vox_machina.models import MergedSegment, SpeakerSegment, TranscriptSegment


def test_speaker_segment_creation() -> None:
    segment = SpeakerSegment(start=0.0, end=5.0, speaker="SPEAKER_00")
    assert segment.speaker == "SPEAKER_00"


def test_merged_segment_creation() -> None:
    segment = MergedSegment(start=0.0, end=1.5, text="Hello", speaker="SPEAKER_00")
    assert segment.text == "Hello"
    assert segment.speaker == "SPEAKER_00"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_models.py -v
```

Expected: FAIL (SpeakerSegment, MergedSegment not found)

- [ ] **Step 3: Add models**

Add to `src/vox_machina/models.py`:

```python
class SpeakerSegment(BaseModel):
    start: float
    end: float
    speaker: str

    @model_validator(mode="after")
    def validate_times(self) -> "SpeakerSegment":
        if self.start < 0:
            raise ValueError("start must be non-negative")
        if self.end < self.start:
            raise ValueError("end must be >= start")
        return self


class MergedSegment(BaseModel):
    start: float
    end: float
    text: str
    speaker: str
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_models.py -v
```

Expected: all 5 PASS

- [ ] **Step 5: Commit**

```bash
git add src/vox_machina/models.py tests/test_models.py
git commit -m "feat: add SpeakerSegment and MergedSegment models"
```

---

### Task 2.2: Merge Logic

**Files:**
- Create: `src/vox_machina/merge.py`
- Create: `tests/test_merge.py`

- [ ] **Step 1: Write failing tests**

`tests/test_merge.py`:

```python
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
    result = merge_segments([], [SpeakerSegment(start=0.0, end=5.0, speaker="SPEAKER_00")])
    assert result == []
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_merge.py -v
```

Expected: FAIL (cannot import `vox_machina.merge`)

- [ ] **Step 3: Implement merge logic**

`src/vox_machina/merge.py`:

```python
from vox_machina.models import MergedSegment, SpeakerSegment, TranscriptSegment


def _overlap(t_start: float, t_end: float, s_start: float, s_end: float) -> float:
    overlap_start = max(t_start, s_start)
    overlap_end = min(t_end, s_end)
    return max(0.0, overlap_end - overlap_start)


def merge_segments(
    transcripts: list[TranscriptSegment],
    speakers: list[SpeakerSegment],
) -> list[MergedSegment]:
    merged: list[MergedSegment] = []
    for t in transcripts:
        best_speaker = "UNKNOWN"
        best_overlap = 0.0
        for s in speakers:
            ov = _overlap(t.start, t.end, s.start, s.end)
            if ov > best_overlap:
                best_overlap = ov
                best_speaker = s.speaker
        merged.append(
            MergedSegment(start=t.start, end=t.end, text=t.text, speaker=best_speaker)
        )
    return merged
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_merge.py -v
```

Expected: all 5 PASS

- [ ] **Step 5: Commit**

```bash
git add src/vox_machina/merge.py tests/test_merge.py
git commit -m "feat: add merge logic to align transcripts with speaker segments"
```

---

### Task 2.3: Diarization Module

**Files:**
- Create: `src/vox_machina/diarize.py`
- Modify: `pyproject.toml` (add speechbrain, torchaudio)

- [ ] **Step 1: Add speechbrain and torchaudio dependencies**

Add to `[project.dependencies]` in `pyproject.toml`:

```toml
"speechbrain>=1.0.0",
"torchaudio>=2.0.0",
```

Then sync:

```bash
uv sync
```

- [ ] **Step 2: Implement diarization module**

`src/vox_machina/diarize.py`:

```python
import logging

import torchaudio
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from vox_machina.models import SpeakerSegment

logger = logging.getLogger(__name__)


def diarize_audio(audio_path: str) -> list[SpeakerSegment]:
    """Run speaker diarization on an audio file.

    Returns an empty list if diarization fails (e.g. audio too short),
    which causes the merge step to label everything as UNKNOWN. This is
    the expected fallback for single-speaker recordings.

    Note: The exact speechbrain diarization API may vary by version.
    Consult speechbrain docs for the SpeakerDiarization class. The contract
    is: takes an audio file path, returns a list of SpeakerSegment.
    """
    console = Console()

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Running speaker diarization..."),
        ) as progress:
            progress.add_task("diarizing", total=None)

            # speechbrain expects 16kHz mono audio
            signal, sample_rate = torchaudio.load(audio_path)

            if sample_rate != 16000:
                resampler = torchaudio.transforms.Resample(sample_rate, 16000)
                signal = resampler(signal)

            if signal.shape[0] > 1:
                signal = signal.mean(dim=0, keepdim=True)

            from speechbrain.inference.speaker import SpeakerDiarization

            diarization = SpeakerDiarization.from_hparams(
                source="speechbrain/spkrec-ecapa-voxceleb",
            )
            result = diarization.diarize_file(audio_path)

            segments: list[SpeakerSegment] = []
            for seg in result:
                segments.append(
                    SpeakerSegment(
                        start=seg["start"],
                        end=seg["stop"],
                        speaker=f"SPEAKER_{seg['label']:02d}",
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
```

- [ ] **Step 3: Verify import works**

```bash
uv run python -c "from vox_machina.diarize import diarize_audio; print('OK')"
```

Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add src/vox_machina/diarize.py pyproject.toml uv.lock
git commit -m "feat: add speechbrain speaker diarization module"
```

---

### Task 2.4: Upgrade Formatter for Speakers

**Files:**
- Modify: `src/vox_machina/format.py`
- Modify: `tests/test_format.py`

- [ ] **Step 1: Add failing tests for speaker-aware formatting**

Add to `tests/test_format.py` (update imports to include `format_transcript_with_speakers` and `MergedSegment`):

```python
from vox_machina.format import format_transcript_with_speakers
from vox_machina.models import MergedSegment


def test_speaker_formatting() -> None:
    segments = [
        MergedSegment(start=1.0, end=3.0, text="Hello world", speaker="SPEAKER_00"),
    ]
    result = format_transcript_with_speakers(
        segments, source_filename="meeting.m4a", duration_seconds=180.0
    )

    assert "**SPEAKER_00** (00:00:01)" in result
    assert "Hello world" in result


def test_consecutive_same_speaker_segments_are_grouped() -> None:
    segments = [
        MergedSegment(start=0.0, end=1.0, text="Hello", speaker="SPEAKER_00"),
        MergedSegment(start=1.0, end=2.0, text="world", speaker="SPEAKER_00"),
    ]
    result = format_transcript_with_speakers(
        segments, source_filename="test.wav", duration_seconds=2.0
    )

    assert result.count("**SPEAKER_00**") == 1
    assert "Hello world" in result


def test_different_speakers_get_separate_blocks() -> None:
    segments = [
        MergedSegment(start=0.0, end=1.0, text="Hello", speaker="SPEAKER_00"),
        MergedSegment(start=1.0, end=2.0, text="Hi there", speaker="SPEAKER_01"),
    ]
    result = format_transcript_with_speakers(
        segments, source_filename="test.wav", duration_seconds=2.0
    )

    assert "**SPEAKER_00**" in result
    assert "**SPEAKER_01**" in result
    assert result.index("SPEAKER_00") < result.index("SPEAKER_01")
```

- [ ] **Step 2: Run tests to verify new tests fail**

```bash
uv run pytest tests/test_format.py -v
```

Expected: new tests FAIL, old tests still PASS

- [ ] **Step 3: Replace formatter with speaker-aware version**

Replace `format_transcript()` with `format_transcript_with_speakers()` in `src/vox_machina/format.py`:

```python
from vox_machina.models import MergedSegment


def format_transcript_with_speakers(
    segments: list[MergedSegment],
    source_filename: str,
    duration_seconds: float,
) -> str:
    lines: list[str] = [
        f"# Transcript: {source_filename}",
        "",
        f"**Date:** {date.today().isoformat()}",
        f"**Duration:** {_format_time(duration_seconds)}",
        "",
        "---",
    ]

    grouped = _group_consecutive_speakers(segments)
    for speaker, start, text in grouped:
        lines.append("")
        lines.append(f"**{speaker}** ({_format_time(start)})")
        lines.append(text)

    lines.append("")
    return "\n".join(lines)


def _group_consecutive_speakers(
    segments: list[MergedSegment],
) -> list[tuple[str, float, str]]:
    if not segments:
        return []

    groups: list[tuple[str, float, str]] = []
    current_speaker = segments[0].speaker
    current_start = segments[0].start
    current_texts: list[str] = [segments[0].text]

    for seg in segments[1:]:
        if seg.speaker == current_speaker:
            current_texts.append(seg.text)
        else:
            groups.append((current_speaker, current_start, " ".join(current_texts)))
            current_speaker = seg.speaker
            current_start = seg.start
            current_texts = [seg.text]

    groups.append((current_speaker, current_start, " ".join(current_texts)))
    return groups
```

- [ ] **Step 4: Run all format tests**

```bash
uv run pytest tests/test_format.py -v
```

Expected: all 7 PASS (4 old + 3 new)

- [ ] **Step 5: Commit**

```bash
git add src/vox_machina/format.py tests/test_format.py
git commit -m "feat: add speaker-aware markdown formatting with grouping"
```

---

### Task 2.5: Wire Diarization into CLI

**Files:**
- Modify: `src/vox_machina/cli.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Add failing test for diarized transcription**

Add to `tests/test_cli.py`:

```python
@patch("vox_machina.cli.diarize_audio")
@patch("vox_machina.cli.transcribe_audio")
def test_transcribe_command_with_diarization(
    mock_transcribe: MagicMock,
    mock_diarize: MagicMock,
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

    result = runner.invoke(app, [str(audio_file)])

    assert result.exit_code == 0
    content = (tmp_path / "meeting.md").read_text()
    assert "SPEAKER_00" in content
    assert "SPEAKER_01" in content
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run pytest tests/test_cli.py::test_transcribe_command_with_diarization -v
```

Expected: FAIL

- [ ] **Step 3: Update CLI to use diarization + merge**

Replace `src/vox_machina/cli.py` main callback:

```python
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console

from vox_machina.diarize import diarize_audio
from vox_machina.format import format_transcript_with_speakers
from vox_machina.merge import merge_segments
from vox_machina.transcribe import transcribe_audio

app = typer.Typer(add_completion=False)
console = Console()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    file: Annotated[Optional[Path], typer.Argument(help="Audio file to transcribe")] = None,
    output: Annotated[Optional[Path], typer.Option(help="Output file path")] = None,
    model: Annotated[str, typer.Option(help="Whisper model size")] = "large-v3",
) -> None:
    """vox: local voice transcription with speaker diarization."""
    if ctx.invoked_subcommand is not None:
        return

    if file is None:
        console.print("[red]Error: please provide an audio file to transcribe.[/red]")
        raise typer.Exit(1)

    if not file.exists():
        console.print(f"[red]Error: file not found: {file}[/red]")
        raise typer.Exit(1)

    segments, duration = transcribe_audio(str(file), model_size=model)
    speaker_segments = diarize_audio(str(file))
    merged = merge_segments(segments, speaker_segments)
    markdown = format_transcript_with_speakers(
        merged, source_filename=file.name, duration_seconds=duration
    )

    output_path = output or file.with_suffix(".md")
    output_path.write_text(markdown)
    console.print(f"[green]Transcript saved to {output_path}[/green]")
```

- [ ] **Step 4: Run all tests + lint**

```bash
uv run pytest -v
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
```

Expected: all pass

- [ ] **Step 5: Commit**

```bash
git add src/vox_machina/cli.py tests/test_cli.py
git commit -m "feat: integrate speaker diarization into transcription pipeline"
```

---

## v0.3.0: Speaker Rename (Bicycle)

**Goal:** `vox rename meeting.md` walks you through each speaker interactively, or accepts names via flag. Makes transcripts human-readable.

**Prerequisite:** v0.2.0 complete

---

### Task 3.1: Rename Module

**Files:**
- Create: `src/vox_machina/rename.py`
- Create: `tests/test_rename.py`

- [ ] **Step 1: Write failing tests**

`tests/test_rename.py`:

```python
from vox_machina.rename import (
    extract_first_quotes,
    extract_speakers,
    parse_speaker_mapping,
    rename_speakers,
)


def test_extract_speakers_finds_all_speakers() -> None:
    transcript = (
        "**SPEAKER_00** (00:00:01)\nHello\n\n"
        "**SPEAKER_01** (00:00:04)\nHi there\n\n"
        "**SPEAKER_00** (00:00:08)\nHow are you?\n"
    )
    speakers = extract_speakers(transcript)
    assert speakers == ["SPEAKER_00", "SPEAKER_01"]


def test_extract_speakers_returns_empty_for_no_speakers() -> None:
    transcript = "Just some text without speakers."
    assert extract_speakers(transcript) == []


def test_rename_speakers_replaces_all_occurrences() -> None:
    transcript = (
        "**SPEAKER_00** (00:00:01)\nHello\n\n"
        "**SPEAKER_01** (00:00:04)\nHi\n\n"
        "**SPEAKER_00** (00:00:08)\nBye\n"
    )
    mapping = {"SPEAKER_00": "Niklas", "SPEAKER_01": "Alex"}
    result = rename_speakers(transcript, mapping)

    assert "**Niklas**" in result
    assert "**Alex**" in result
    assert "SPEAKER_00" not in result
    assert "SPEAKER_01" not in result


def test_rename_speakers_preserves_unmapped_speakers() -> None:
    transcript = "**SPEAKER_00** (00:00:01)\nHello\n\n**SPEAKER_01** (00:00:04)\nHi\n"
    mapping = {"SPEAKER_00": "Niklas"}
    result = rename_speakers(transcript, mapping)

    assert "**Niklas**" in result
    assert "**SPEAKER_01**" in result


def test_parse_speaker_mapping() -> None:
    raw = "SPEAKER_00=Niklas,SPEAKER_01=Alex"
    result = parse_speaker_mapping(raw)
    assert result == {"SPEAKER_00": "Niklas", "SPEAKER_01": "Alex"}


def test_extract_first_quotes() -> None:
    transcript = (
        "**SPEAKER_00** (00:00:01)\nFirst thing\n\n"
        "**SPEAKER_01** (00:00:04)\nAnother thing\n\n"
        "**SPEAKER_00** (00:00:08)\nSecond thing\n"
    )
    speakers = extract_speakers(transcript)
    first_quotes = extract_first_quotes(transcript, speakers)
    assert first_quotes["SPEAKER_00"] == "First thing"
    assert first_quotes["SPEAKER_01"] == "Another thing"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_rename.py -v
```

Expected: FAIL (cannot import `vox_machina.rename`)

- [ ] **Step 3: Implement rename module**

`src/vox_machina/rename.py`:

```python
import re


def extract_speakers(transcript: str) -> list[str]:
    pattern = re.compile(r"\*\*(SPEAKER_\d+)\*\*")
    seen: set[str] = set()
    ordered: list[str] = []
    for match in pattern.finditer(transcript):
        speaker = match.group(1)
        if speaker not in seen:
            seen.add(speaker)
            ordered.append(speaker)
    return ordered


def extract_first_quotes(
    transcript: str, speakers: list[str]
) -> dict[str, str]:
    quotes: dict[str, str] = {}
    for speaker in speakers:
        pattern = re.compile(
            rf"\*\*{re.escape(speaker)}\*\*\s*\([^)]+\)\n(.+)"
        )
        match = pattern.search(transcript)
        if match:
            quotes[speaker] = match.group(1).strip()
    return quotes


def rename_speakers(transcript: str, mapping: dict[str, str]) -> str:
    result = transcript
    for old_name, new_name in mapping.items():
        result = result.replace(f"**{old_name}**", f"**{new_name}**")
    return result


def parse_speaker_mapping(raw: str) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for pair in raw.split(","):
        key, value = pair.strip().split("=", 1)
        mapping[key.strip()] = value.strip()
    return mapping
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_rename.py -v
```

Expected: all 6 PASS

- [ ] **Step 5: Commit**

```bash
git add src/vox_machina/rename.py tests/test_rename.py
git commit -m "feat: add speaker extraction, renaming, and quote preview"
```

---

### Task 3.2: Wire Rename into CLI

**Files:**
- Modify: `src/vox_machina/cli.py`
- Modify: `tests/test_cli.py`
- Modify: `pyproject.toml` (add questionary dependency)

- [ ] **Step 1: Add questionary dependency**

Add to `[project.dependencies]` in `pyproject.toml`:

```toml
"questionary>=2.1.0",
```

Then sync:

```bash
uv sync
```

- [ ] **Step 2: Add failing test for rename command**

Add to `tests/test_cli.py`:

```python
def test_rename_command_non_interactive(tmp_path: Path) -> None:
    transcript_file = tmp_path / "test.md"
    transcript_file.write_text(
        "# Transcript: test.wav\n\n"
        "**SPEAKER_00** (00:00:01)\nHello\n\n"
        "**SPEAKER_01** (00:00:04)\nHi\n"
    )

    result = runner.invoke(
        app, ["rename", str(transcript_file), "--speakers", "SPEAKER_00=Niklas,SPEAKER_01=Alex"]
    )

    assert result.exit_code == 0
    content = transcript_file.read_text()
    assert "**Niklas**" in content
    assert "**Alex**" in content
    assert "SPEAKER_00" not in content
```

- [ ] **Step 3: Run test to verify it fails**

```bash
uv run pytest tests/test_cli.py::test_rename_command_non_interactive -v
```

Expected: FAIL

- [ ] **Step 4: Add rename command to CLI**

Add to `src/vox_machina/cli.py`:

```python
import questionary

from vox_machina.rename import (
    extract_first_quotes,
    extract_speakers,
    parse_speaker_mapping,
    rename_speakers,
)


@app.command()
def rename(
    file: Annotated[Path, typer.Argument(help="Transcript .md file")],
    speakers: Annotated[Optional[str], typer.Option(
        help="Speaker mapping, e.g. 'SPEAKER_00=Niklas,SPEAKER_01=Alex'"
    )] = None,
    output: Annotated[Optional[Path], typer.Option(
        help="Output file path (default: overwrite input)"
    )] = None,
) -> None:
    """Replace generic speaker labels with real names."""
    if not file.exists():
        console.print(f"[red]Error: file not found: {file}[/red]")
        raise typer.Exit(1)

    transcript = file.read_text()

    if speakers:
        mapping = parse_speaker_mapping(speakers)
    else:
        detected = extract_speakers(transcript)
        if not detected:
            console.print("[yellow]No speaker labels found in transcript.[/yellow]")
            raise typer.Exit(0)

        first_quotes = extract_first_quotes(transcript, detected)
        mapping = {}
        for speaker in detected:
            quote = first_quotes.get(speaker, "(no quote found)")
            name = questionary.text(
                f'{speaker} said: "{quote}"\nWho is this?',
            ).ask()
            if name:
                mapping[speaker] = name

    result = rename_speakers(transcript, mapping)
    output_path = output or file
    output_path.write_text(result)
    console.print(f"[green]Speakers renamed in {output_path}[/green]")
```

- [ ] **Step 5: Run all tests + lint**

```bash
uv run pytest -v
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
```

Expected: all pass

- [ ] **Step 6: Commit**

```bash
git add src/vox_machina/cli.py tests/test_cli.py pyproject.toml uv.lock
git commit -m "feat: add interactive speaker rename command"
```

---

## v0.4.0: Summarization (Motorcycle)

**Goal:** `vox summarize meeting.md` produces structured meeting notes via local Ollama. Supports custom prompt templates and warns about context window limits.

**Prerequisite:** v0.3.0 complete

---

### Task 4.1: Summarization Module

**Files:**
- Create: `src/vox_machina/summarize.py`
- Create: `src/vox_machina/prompts/__init__.py`
- Create: `src/vox_machina/prompts/meeting_notes.md`
- Create: `tests/test_summarize.py`
- Modify: `pyproject.toml` (add ollama dependency)

- [ ] **Step 1: Add ollama dependency**

Add to `[project.dependencies]` in `pyproject.toml`:

```toml
"ollama>=0.4.0",
```

Then sync:

```bash
uv sync
```

- [ ] **Step 2: Create default prompt template**

`src/vox_machina/prompts/__init__.py`: empty file.

`src/vox_machina/prompts/meeting_notes.md`:

```markdown
You are summarizing a meeting transcript. Produce structured meeting notes in markdown format.

## Instructions

Analyze the following transcript and extract:

1. **Key Topics Discussed** - main subjects covered in the meeting
2. **Decisions Made** - any decisions that were agreed upon
3. **Action Items** - tasks assigned to specific people (include the person's name where identifiable)
4. **Open Questions** - unresolved questions or topics that need follow-up

Be concise. Use bullet points. Attribute statements and action items to specific speakers where possible.

## Transcript

{transcript}
```

- [ ] **Step 3: Write failing tests**

`tests/test_summarize.py`:

```python
from pathlib import Path
from unittest.mock import MagicMock, patch

from vox_machina.summarize import build_prompt, load_prompt_template, summarize_transcript


def test_load_default_prompt_template() -> None:
    template = load_prompt_template()
    assert "{transcript}" in template
    assert "Key Topics" in template


def test_load_custom_prompt_template(tmp_path: Path) -> None:
    custom = tmp_path / "custom.md"
    custom.write_text("Summarize this: {transcript}")
    template = load_prompt_template(str(custom))
    assert template == "Summarize this: {transcript}"


def test_build_prompt_injects_transcript() -> None:
    template = "Summary of: {transcript}"
    result = build_prompt(template, "Hello world conversation")
    assert result == "Summary of: Hello world conversation"


@patch("vox_machina.summarize.ollama")
def test_summarize_transcript_calls_ollama(mock_ollama: MagicMock) -> None:
    mock_ollama.chat.return_value = {"message": {"content": "## Summary\nStuff happened"}}

    result = summarize_transcript("Some transcript text", model="llama3.1")

    mock_ollama.chat.assert_called_once()
    call_kwargs = mock_ollama.chat.call_args
    assert call_kwargs.kwargs["model"] == "llama3.1"
    assert "Some transcript text" in call_kwargs.kwargs["messages"][0]["content"]
    assert result == "## Summary\nStuff happened"


@patch("vox_machina.summarize.ollama")
def test_summarize_transcript_with_custom_prompt(
    mock_ollama: MagicMock, tmp_path: Path
) -> None:
    mock_ollama.chat.return_value = {"message": {"content": "Custom summary"}}
    custom = tmp_path / "custom.md"
    custom.write_text("Just summarize: {transcript}")

    result = summarize_transcript(
        "Transcript text", model="llama3.1", prompt_path=str(custom)
    )

    call_content = mock_ollama.chat.call_args.kwargs["messages"][0]["content"]
    assert call_content == "Just summarize: Transcript text"
    assert result == "Custom summary"
```

- [ ] **Step 4: Run tests to verify they fail**

```bash
uv run pytest tests/test_summarize.py -v
```

Expected: FAIL (cannot import `vox_machina.summarize`)

- [ ] **Step 5: Implement summarization module**

`src/vox_machina/summarize.py`:

```python
from importlib.resources import files
from pathlib import Path

import ollama
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn


def load_prompt_template(prompt_path: str | None = None) -> str:
    if prompt_path:
        return Path(prompt_path).read_text()
    default = files("vox_machina.prompts").joinpath("meeting_notes.md")
    return default.read_text()


def build_prompt(template: str, transcript: str) -> str:
    return template.replace("{transcript}", transcript)


def verify_model_available(model: str) -> None:
    """Check that the requested Ollama model is pulled locally."""
    try:
        models = ollama.list()
        available = [m["name"].split(":")[0] for m in models.get("models", [])]
        if model not in available:
            console = Console()
            console.print(
                f"[red]Error: model '{model}' not found locally. "
                f"Pull it first with: ollama pull {model}[/red]"
            )
            console.print(f"[dim]Available models: {', '.join(available) or '(none)'}[/dim]")
            raise SystemExit(1)
    except ConnectionError:
        console = Console()
        console.print(
            "[red]Error: cannot connect to Ollama. "
            "Make sure it is running: ollama serve[/red]"
        )
        raise SystemExit(1)


def check_context_window(prompt: str, model: str) -> None:
    """Warn if the prompt is likely too large for the model's context window."""
    estimated_tokens = len(prompt) // 4
    try:
        model_info = ollama.show(model)
        num_ctx = int(model_info.get("parameters", {}).get("num_ctx", 2048))
    except Exception:
        num_ctx = 2048

    if estimated_tokens > num_ctx:
        console = Console()
        console.print(
            f"[yellow]Warning: transcript is ~{estimated_tokens} tokens, "
            f"but {model}'s context window is {num_ctx} tokens. "
            f"Consider increasing num_ctx in your Ollama modelfile.[/yellow]"
        )


def summarize_transcript(
    transcript: str,
    model: str = "llama3.1",
    prompt_path: str | None = None,
) -> str:
    verify_model_available(model)

    template = load_prompt_template(prompt_path)
    prompt = build_prompt(template, transcript)

    check_context_window(prompt, model)

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]Summarizing with Ollama..."),
    ) as progress:
        progress.add_task("summarizing", total=None)
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )

    return response["message"]["content"]
```

- [ ] **Step 6: Run tests to verify they pass**

```bash
uv run pytest tests/test_summarize.py -v
```

Expected: all 5 PASS

- [ ] **Step 7: Commit**

```bash
git add src/vox_machina/summarize.py src/vox_machina/prompts/ tests/test_summarize.py pyproject.toml uv.lock
git commit -m "feat: add Ollama-based transcript summarization with prompt templates"
```

---

### Task 4.2: Wire Summarize into CLI

**Files:**
- Modify: `src/vox_machina/cli.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Add failing test for summarize command**

Add to `tests/test_cli.py`:

```python
@patch("vox_machina.cli.summarize_transcript")
def test_summarize_command_creates_summary_file(
    mock_summarize: MagicMock, tmp_path: Path
) -> None:
    mock_summarize.return_value = "## Summary\nKey topics discussed."

    transcript_file = tmp_path / "meeting.md"
    transcript_file.write_text("# Transcript: meeting.m4a\n\nSome transcript content.")

    result = runner.invoke(app, ["summarize", str(transcript_file)])

    assert result.exit_code == 0
    summary_file = tmp_path / "meeting-summary.md"
    assert summary_file.exists()
    assert "Key topics discussed" in summary_file.read_text()
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run pytest tests/test_cli.py::test_summarize_command_creates_summary_file -v
```

Expected: FAIL

- [ ] **Step 3: Add summarize command to CLI**

Add to `src/vox_machina/cli.py`:

```python
from vox_machina.summarize import summarize_transcript


@app.command()
def summarize(
    file: Annotated[Path, typer.Argument(help="Transcript .md file to summarize")],
    model: Annotated[str, typer.Option(help="Ollama model name")] = "llama3.1",
    prompt: Annotated[Optional[Path], typer.Option(help="Custom prompt template (.md)")] = None,
    output: Annotated[Optional[Path], typer.Option(help="Output file path")] = None,
) -> None:
    """Summarize a transcript using a local Ollama model."""
    if not file.exists():
        console.print(f"[red]Error: file not found: {file}[/red]")
        raise typer.Exit(1)

    transcript = file.read_text()
    prompt_path = str(prompt) if prompt else None
    summary = summarize_transcript(transcript, model=model, prompt_path=prompt_path)

    output_path = output or file.with_name(f"{file.stem}-summary.md")
    output_path.write_text(summary)
    console.print(f"[green]Summary saved to {output_path}[/green]")
```

- [ ] **Step 4: Run all tests + lint**

```bash
uv run pytest -v
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
```

Expected: all pass

- [ ] **Step 5: Commit**

```bash
git add src/vox_machina/cli.py tests/test_cli.py
git commit -m "feat: add summarize command to CLI"
```

---

## v0.5.0: Polish (Banner + UX)

**Goal:** Polished terminal experience with ASCII banner and consistent rich output across all commands.

**Prerequisite:** v0.4.0 complete

---

### Task 5.1: ASCII Banner

**Files:**
- Create: `src/vox_machina/banner.py`

- [ ] **Step 1: Implement banner module**

`src/vox_machina/banner.py`:

```python
from rich.console import Console

BANNER = r"""
 [bold cyan]██╗   ██╗ ██████╗ ██╗  ██╗[/bold cyan]
 [bold cyan]██║   ██║██╔═══██╗╚██╗██╔╝[/bold cyan]
 [bold cyan]██║   ██║██║   ██║ ╚███╔╝[/bold cyan]
 [bold cyan]╚██╗ ██╔╝██║   ██║ ██╔██╗[/bold cyan]
 [bold cyan] ╚████╔╝ ╚██████╔╝██╔╝ ██╗[/bold cyan]
 [bold cyan]  ╚═══╝   ╚═════╝ ╚═╝  ╚═╝[/bold cyan]
   [dim]local voice transcription[/dim]
"""


def print_banner() -> None:
    console = Console()
    console.print(BANNER)
```

- [ ] **Step 2: Verify it renders**

```bash
uv run python -c "from vox_machina.banner import print_banner; print_banner()"
```

Expected: colored ASCII art banner in terminal

- [ ] **Step 3: Commit**

```bash
git add src/vox_machina/banner.py
git commit -m "feat: add ASCII art banner"
```

---

### Task 5.2: Wire Banner into CLI

**Files:**
- Modify: `src/vox_machina/cli.py`

- [ ] **Step 1: Add banner to CLI callback**

Add import and call at the start of the `main` callback:

```python
from vox_machina.banner import print_banner

# Inside main(), as the first line:
print_banner()
```

- [ ] **Step 2: Run all tests + lint**

```bash
uv run pytest -v
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
```

Expected: all pass

- [ ] **Step 3: Commit**

```bash
git add src/vox_machina/cli.py
git commit -m "feat: show ASCII banner on CLI startup"
```

- [ ] **Step 4: Final smoke test**

```bash
uv run vox --help
```

Expected: banner displays, then help text with all three commands (rename, summarize).

---

## v0.6.0: Summaries+ (Multiple Templates + Chunked Summarization)

**Goal:** Ship built-in prompt templates for common scenarios (standups, interviews) and handle long recordings via chunked summarization so users never hit context window limits.

**Prerequisite:** v0.5.0 complete

---

### Task 6.1: Additional Prompt Templates

**Files:**
- Create: `src/vox_machina/prompts/standup.md`
- Create: `src/vox_machina/prompts/interview.md`
- Modify: `src/vox_machina/summarize.py` (add template discovery)
- Create: `tests/test_prompt_templates.py`

**What this delivers:**

- `vox summarize meeting.md --prompt standup` uses the standup template
- `vox summarize meeting.md --prompt interview` uses the interview template
- `vox summarize meeting.md --prompt meeting_notes` stays the default
- `vox summarize meeting.md --prompt /path/to/custom.md` still works for custom templates

The `--prompt` flag should accept either a built-in template name (without extension) or a file path. The `load_prompt_template()` function needs to be updated to check built-in templates first, then fall back to file path.

**Standup template** should produce:
- Per-person updates (what they did, what they're doing next)
- Blockers
- Action items

**Interview template** should produce:
- Key insights
- Notable quotes (with speaker attribution)
- Themes and patterns
- Follow-up questions

- [ ] **Step 1: Write failing tests for template discovery**
- [ ] **Step 2: Run tests to verify they fail**
- [ ] **Step 3: Create standup.md template**
- [ ] **Step 4: Create interview.md template**
- [ ] **Step 5: Update load_prompt_template() to support name-based lookup**
- [ ] **Step 6: Run tests to verify they pass**
- [ ] **Step 7: Commit**

---

### Task 6.2: Chunked Summarization

**Files:**
- Create: `src/vox_machina/chunk.py`
- Modify: `src/vox_machina/summarize.py`
- Create: `tests/test_chunk.py`

**What this delivers:**

When a transcript exceeds the model's context window, the summarization pipeline automatically:

1. Splits the transcript into chunks that fit within the context window (with some overlap for continuity)
2. Summarizes each chunk individually using the same prompt template
3. Runs a final "merge summaries" pass that combines chunk summaries into one cohesive output

The user sees a note in the terminal: `"Transcript is long, summarizing in 4 chunks..."` but the output is a single summary file, same as before.

**Key design decisions:**
- Chunk boundaries should respect speaker turns (never split mid-sentence or mid-speaker-block)
- Overlap between chunks (~200 tokens) provides context continuity
- The merge pass uses a separate internal prompt: "Combine these partial summaries into a single coherent summary"
- Token estimation: ~4 characters per token (rough but sufficient for deciding chunk size)

- [ ] **Step 1: Write failing tests for chunk splitting logic**
- [ ] **Step 2: Run tests to verify they fail**
- [ ] **Step 3: Implement chunk.py (split_transcript, merge_summaries)**
- [ ] **Step 4: Run tests to verify they pass**
- [ ] **Step 5: Integrate chunked mode into summarize_transcript()**
- [ ] **Step 6: Update CLI test to verify chunked mode triggers for long transcripts**
- [ ] **Step 7: Run full test suite + lint**
- [ ] **Step 8: Commit**

---

## v0.7.0: Obsidian Integration

**Goal:** Output transcripts and summaries in Obsidian-ready format with YAML frontmatter, tags, and proper structure for knowledge base integration.

**Prerequisite:** v0.6.0 complete

---

### Task 7.1: Obsidian Formatter

**Files:**
- Create: `src/vox_machina/obsidian.py`
- Create: `tests/test_obsidian.py`

**What this delivers:**

A `--obsidian` flag on both the transcribe and summarize commands that outputs markdown with YAML frontmatter.

**Transcript output with `--obsidian`:**

```markdown
---
type: transcript
date: 2026-05-21
duration: "00:45:12"
source: meeting.m4a
speakers:
  - SPEAKER_00
  - SPEAKER_01
tags:
  - transcript
---

# Transcript: meeting.m4a

...
```

**Summary output with `--obsidian`:**

```markdown
---
type: summary
date: 2026-05-21
source: meeting.md
model: llama3.1
prompt: meeting_notes
tags:
  - summary
  - meeting-notes
---

# Summary: meeting.md

...
```

After `vox rename`, the speakers list in the frontmatter should also be updated (the rename command already modifies the file, so it should update the frontmatter too).

**Key design decisions:**
- Frontmatter is YAML, parsed and written with a lightweight approach (no heavy YAML library needed, the structure is simple and predictable)
- Tags are auto-generated from the template type (meeting-notes, standup, interview)
- The `--obsidian` flag works with all commands: `vox`, `vox rename`, `vox summarize`
- When used with the `/obsidian` skill, formatting conventions from that skill should be followed

- [ ] **Step 1: Write failing tests for obsidian frontmatter generation**
- [ ] **Step 2: Run tests to verify they fail**
- [ ] **Step 3: Implement obsidian.py (generate_frontmatter, format_with_frontmatter)**
- [ ] **Step 4: Run tests to verify they pass**
- [ ] **Step 5: Wire --obsidian flag into CLI (transcribe command)**
- [ ] **Step 6: Wire --obsidian flag into CLI (summarize command)**
- [ ] **Step 7: Update rename command to also update frontmatter speakers list**
- [ ] **Step 8: Add CLI tests for --obsidian flag**
- [ ] **Step 9: Run full test suite + lint**
- [ ] **Step 10: Commit**
