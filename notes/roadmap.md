# vox-machina Roadmap

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

Each slice is independently useful and ends with passing tests, lint, and a commit.

| Slice | Version | What it delivers | Status |
|-------|---------|-----------------|--------|
| Skateboard | v0.2.0 | `vox transcribe file.m4a` produces timestamped transcript | Done |
| Scooter | v0.3.0 | Adds speaker diarization (SPEAKER_00, SPEAKER_01, ...) | Done |
| Bicycle | v0.4.0 | `vox rename` for interactive speaker label replacement | Done |
| Motorcycle | v0.5.0 | `vox summarize` via local Ollama with prompt templates | Done |
| Polish | v0.6.0 | ASCII banner, config questionnaire, polished rich UX | |
| Split CLI | v0.7.0 | `vox` for audio, `machina` for text processing | |
| Summaries+ | v0.8.0 | Multiple prompt templates + chunked summarization for long recordings | |
| Obsidian | v0.9.0 | Obsidian-ready output with frontmatter, tags, wikilinks | |
| Backends | v0.10.0 | Alternative model backends (MLX, other providers) | |

---

## v0.6.0: Polish (Banner + UX)

**Goal:** Polished terminal experience with ASCII banner, configuration questionnaire, and consistent rich output across all commands.

**Prerequisite:** v0.5.0 complete

---

### Task 6.1: ASCII Banner

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

### Task 6.2: Wire Banner into CLI

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

Expected: banner displays, then help text with all three commands (transcribe, rename, summarize).

---

### Task 6.3: Configuration Questionnaire

**Files:**
- Create: `src/vox_machina/config.py`
- Modify: `src/vox_machina/cli.py`

**What this delivers:**

A `vox config` command that walks the user through setup:
- Pick default Ollama model from locally available ones (shows name, size, parameter count)
- Pick default Whisper model size (small, medium, large-v3)
- Config saved to `~/.config/vox-machina/config.json`

First run of `vox summarize` without a config triggers the questionnaire automatically.
`--model` flags still work as overrides.

- [ ] **Step 1: Write tests for config loading/saving**
- [ ] **Step 2: Implement config.py**
- [ ] **Step 3: Add vox config command**
- [ ] **Step 4: Wire config defaults into transcribe and summarize**
- [ ] **Step 5: Run full test suite + lint**
- [ ] **Step 6: Commit**

---

### Task 6.4: Suppress noisy warnings

Suppress the `objc` AVF duplicate class warnings and pyannote `UserWarning` stderr noise.

- [ ] **Step 1: Investigate and implement suppression**
- [ ] **Step 2: Commit**

---

## v0.7.0: Split CLI (`vox` + `machina`)

**Goal:** Split the CLI into two entry points that mirror the project name: `vox` for audio operations, `machina` for text processing.

**Prerequisite:** v0.6.0 complete

**What this delivers:**

```
vox transcribe meeting.m4a         # audio -> text (voice)
machina rename meeting.md          # text processing (machine)
machina summarize meeting.md       # text processing (machine)
```

**Key design decisions:**
- Two separate entry points in `pyproject.toml` (`vox` and `machina`)
- Shared internals, just different CLI surfaces
- Each command is self-contained and discoverable via `--help`
- Opens the door for users to install only the part they need (future: optional dependency groups)

- [ ] **Step 1: Create separate typer apps for vox and machina**
- [ ] **Step 2: Move rename and summarize to machina app**
- [ ] **Step 3: Add machina entry point to pyproject.toml**
- [ ] **Step 4: Update tests**
- [ ] **Step 5: Run full test suite + lint**
- [ ] **Step 6: Commit**

---

## v0.8.0: Summaries+ (Multiple Templates + Chunked Summarization)

**Goal:** Ship built-in prompt templates for common scenarios (standups, interviews) and handle long recordings via chunked summarization so users never hit context window limits.

**Prerequisite:** v0.7.0 complete

---

### Task 8.1: Additional Prompt Templates

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

### Task 8.2: Chunked Summarization

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

## v0.9.0: Obsidian Integration

**Goal:** Output transcripts and summaries in Obsidian-ready format with YAML frontmatter, tags, and proper structure for knowledge base integration.

**Prerequisite:** v0.8.0 complete

---

### Task 9.1: Obsidian Formatter

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
model: qwen3.5:9b
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
- The `--obsidian` flag works with all commands: `vox transcribe`, `vox rename`, `vox summarize`
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

---

## v0.10.0: Alternative Model Backends

**Goal:** Explore alternatives to Ollama for local LLM inference, particularly MLX on Apple Silicon. Ollama adds overhead and requires a separate daemon. Direct MLX integration could be faster and simpler on macOS.

**Prerequisite:** v0.9.0 complete

**Areas to investigate:**
- **Ollama with MLX backend**: Ollama may support MLX natively by this point, which would give us the benefits without code changes
- **Direct MLX integration**: Use `mlx-lm` to load and run models directly, skipping the Ollama daemon entirely
- **Other providers**: llama.cpp via Python bindings, vLLM, or similar
- **Provider abstraction**: If we support multiple backends, the summarization module needs a clean interface so backends are swappable

No detailed tasks yet. Scope depends on what the ecosystem looks like when we get here.
