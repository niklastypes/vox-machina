# vox-machina Roadmap

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

Each slice is independently useful and ends with passing tests, lint, and a commit.

## Philosophy

vox-machina is a focused pipeline tool. Audio in, structured markdown artifacts out. Every output is an input for something else (Obsidian vault, agents, other tools). It's not trying to be a second brain or an agent framework. Keep it lean, stable, and well-tested.

## Slices

| Slice | Version | What it delivers |
|-------|---------|-----------------|
| Obsidian | v0.9.0 | Obsidian-ready output with YAML frontmatter |
| Resumable | v0.10.0 | Intermediate artifacts + resumable pipeline |
| Pipeline | v0.11.0 | `vox-machina meeting.m4a` chains all stages |
| Quality | v0.12.0 | Test coverage, error handling, edge cases |
| UX | v0.13.0 | Model info during stages, progress bars, ETAs |
| Backends | v0.14.0 | MLX / llama.cpp as alternatives to Ollama |

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

After `machina label`, the speakers list in the frontmatter should also be updated (the label command already modifies the file, so it should update the frontmatter too).

**Key design decisions:**
- Frontmatter is YAML, parsed and written with a lightweight approach (no heavy YAML library needed, the structure is simple and predictable)
- Tags are auto-generated from the template type (meeting-notes, standup, interview)
- The `--obsidian` flag works with all commands: `vox transcribe`, `machina label`, `machina summarize`
- When used with the `/obsidian` skill, formatting conventions from that skill should be followed

- [ ] **Step 1: Write failing tests for obsidian frontmatter generation**
- [ ] **Step 2: Run tests to verify they fail**
- [ ] **Step 3: Implement obsidian.py (generate_frontmatter, format_with_frontmatter)**
- [ ] **Step 4: Run tests to verify they pass**
- [ ] **Step 5: Wire --obsidian flag into CLI (transcribe command)**
- [ ] **Step 6: Wire --obsidian flag into CLI (summarize command)**
- [ ] **Step 7: Update label command to also update frontmatter speakers list**
- [ ] **Step 8: Add CLI tests for --obsidian flag**
- [ ] **Step 9: Run full test suite + lint**
- [ ] **Step 10: Commit**

---

## v0.10.0: Resumable Pipeline

**Goal:** Save intermediate artifacts after each pipeline stage so work isn't lost on failure, and enable resuming from the last successful step.

**Prerequisite:** v0.9.0 complete

**What this delivers:**

Transcription is the most expensive step (minutes of processing). If diarization or formatting fails afterwards, the user currently loses everything. This slice adds:

1. **Intermediate artifact**: Save raw whisper segments as JSON (`meeting.segments.json`) immediately after transcription succeeds
2. **Resume flag**: `vox transcribe meeting.m4a --resume` skips whisper if segments.json exists, re-runs diarization + merge + format
3. **Stage-by-stage output**: Each pipeline stage writes its output before the next starts

**Pipeline stages:**
```
whisper transcription -> segments.json (saved immediately)
diarization -> speaker_segments.json (saved)
merge + format -> meeting.md (final output)
```

If any stage fails, previous artifacts are preserved and the pipeline can resume.

- [ ] **Step 1: Define intermediate artifact format (JSON schema for segments)**
- [ ] **Step 2: Save segments.json after transcription**
- [ ] **Step 3: Implement --resume flag**
- [ ] **Step 4: Tests**
- [ ] **Step 5: Commit**

---

## v0.11.0: Pipeline Command

**Goal:** A single command that chains the full pipeline with sensible defaults: transcribe, diarize, label, summarize.

**Prerequisite:** v0.10.0 complete (needs intermediate artifacts)

**What this delivers:**

```bash
vox-machina meeting.m4a
```

Third entry point that runs the full pipeline interactively:
1. Transcribe audio (with diarization)
2. If multiple speakers detected, prompt for speaker labels
3. Ask which prompt template to use for summarization
4. Produce final summary artifact

All intermediate artifacts are saved along the way (leverages v0.10.0 resumable pipeline).

**Key design decisions:**
- Interactive by default (questionary prompts for labels and prompt template)
- `--non-interactive` flag for scripting (uses defaults, skips labeling)
- Produces all artifacts: `.segments.json`, `.md` (transcript), `_labeled.md`, `_summarized.md`
- Each artifact can be picked up independently by downstream tools

- [ ] **Step 1: Create vox-machina entry point**
- [ ] **Step 2: Implement pipeline orchestration**
- [ ] **Step 3: Wire questionary prompts for labels and template**
- [ ] **Step 4: Add --non-interactive flag**
- [ ] **Step 5: Tests**
- [ ] **Step 6: Commit**

---

## v0.12.0: Quality

**Goal:** Harden the codebase for everyday reliability. vox-machina is an open-source MIT-licensed project; it should be exemplary.

**Prerequisite:** v0.11.0 complete

**Areas:**
- Increase test coverage (target: 90%+, especially CLI paths and error handling)
- Edge cases: empty audio, very short audio, corrupt files, missing ffmpeg, ollama not running
- Graceful error messages for all failure modes
- Type checking clean (ty strict mode)
- CI pipeline: run tests + lint + type check on every PR

---

## v0.13.0: UX Improvements

**Goal:** Rich terminal feedback during long-running operations. Users should know what's happening, which models are being used, and roughly how long things will take.

**Prerequisite:** v0.12.0 complete

**What this delivers:**

### Model info during stages
Show which model is active at each step:
```
Transcribing with whisper small...
Diarizing with pyannote/speaker-diarization-community-1...
Summarizing with qwen3.5:9b (prompt: retro)...
```

### Progress bars with ETA

All three stages support some form of progress tracking without hacks or upstream changes:

**Transcription (faster-whisper):**
- No built-in progress callback, but `transcribe()` returns a generator of segments
- Each segment has `.end` timestamp, and we know total duration from ffmpeg
- Progress = `segment.end / total_duration` as segments yield
- `log_progress=True` exists but only outputs tqdm bars to stdout (not useful for us)
- ETA estimation: feasible since we know total duration upfront

**Diarization (pyannote):**
- Has a `hook` callback parameter on `Pipeline.apply()` (passed through `**kwargs`)
- Hook signature: `hook(step_name, step_artifact, file=file, total=N, completed=i)`
- Called after major steps: "segmentation" and "embeddings" with `total`/`completed` counters
- No published processing time benchmarks for Apple Silicon, but we could calibrate
- ETA estimation: rough, ratio of audio duration to processing time varies by hardware

**Summarization (ollama):**
- `ollama.chat(stream=True)` returns an iterator of `ChatResponse` chunks
- Each chunk has `message.content` (partial text) and `eval_count` (tokens evaluated)
- Can show live token count or streaming text as it generates
- No way to predict total response length, so no percentage bar, just a "generating..." indicator with token count
- ETA estimation: not feasible (depends on transcript length, model, and prompt)

### Upfront estimation
Based on file duration and a simple benchmark ratio:
```
Estimated processing time: ~25 minutes
  Transcription: ~18 min | Diarization: ~5 min | Summarization: ~2 min
```

Could be calibrated during `vox prepare`:
1. Transcribe a short audio sample, measure the ratio (e.g., "1 min audio = 3 min processing")
2. Run a quick diarization benchmark on the same sample
3. Store ratios in config
4. On subsequent runs, multiply ratio by audio duration for ETA

Without calibration, we can still show progress bars (just no upfront ETA).

---

## v0.14.0: Alternative Model Backends

**Goal:** Explore alternatives to Ollama for local LLM inference, particularly MLX on Apple Silicon. Ollama adds overhead and requires a separate daemon. Direct MLX integration could be faster and simpler on macOS.

**Prerequisite:** v0.13.0 complete

**Areas to investigate:**
- **Ollama with MLX backend**: Ollama may support MLX natively by this point, which would give us the benefits without code changes
- **Direct MLX integration**: Use `mlx-lm` to load and run models directly, skipping the Ollama daemon entirely
- **llama.cpp via Python bindings**: Another option for direct inference
- **Provider abstraction**: If we support multiple backends, the summarization module needs a clean interface so backends are swappable
- **Hardware detection**: Could be a separate library (`hw-probe` or similar) that detects available RAM/GPU and recommends model sizes. Useful for vox-machina and other local AI projects.

No detailed tasks yet. Scope depends on what the ecosystem looks like when we get here.
