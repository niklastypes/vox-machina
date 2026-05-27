# vox-machina Roadmap

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

Each slice is independently useful and ends with passing tests, lint, and a commit.

| Slice | Version | What it delivers | Status |
|-------|---------|-----------------|--------|
| Skateboard | v0.1.0 | `vox file.m4a` produces timestamped transcript | Done |
| Scooter | v0.2.0 | Adds speaker diarization (SPEAKER_00, SPEAKER_01, ...) | Done |
| Bicycle | v0.3.0 | `vox rename` for interactive speaker label replacement | Done |
| Motorcycle | v0.4.0 | `vox summarize` via local Ollama with prompt templates | |
| Polish | v0.5.0 | ASCII banner, polished rich UX throughout | |
| Summaries+ | v0.6.0 | Multiple prompt templates + chunked summarization for long recordings | |
| Obsidian | v0.7.0 | Obsidian-ready output with frontmatter, tags, wikilinks | |

---


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
