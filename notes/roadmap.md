# vox-machina Roadmap

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

Each slice is independently useful and ends with passing tests, lint, and a commit.

| Slice | Version | What it delivers |
|-------|---------|-----------------|
| Obsidian | v0.9.0 | Obsidian-ready output with frontmatter, tags, wikilinks |
| Resumable | v0.10.0 | Intermediate artifacts + resumable pipeline |
| Backends | v0.11.0 | Alternative model backends (MLX, other providers) |

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

## v0.11.0: Alternative Model Backends

**Goal:** Explore alternatives to Ollama for local LLM inference, particularly MLX on Apple Silicon. Ollama adds overhead and requires a separate daemon. Direct MLX integration could be faster and simpler on macOS.

**Prerequisite:** v0.10.0 complete

**Areas to investigate:**
- **Ollama with MLX backend**: Ollama may support MLX natively by this point, which would give us the benefits without code changes
- **Direct MLX integration**: Use `mlx-lm` to load and run models directly, skipping the Ollama daemon entirely
- **Other providers**: llama.cpp via Python bindings, vLLM, or similar
- **Provider abstraction**: If we support multiple backends, the summarization module needs a clean interface so backends are swappable

No detailed tasks yet. Scope depends on what the ecosystem looks like when we get here.
