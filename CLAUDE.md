# vox-machina

🦻 Local voice transcription with speaker diarization and LLM-powered summarization

## Core Identity

vox-machina is a CLI tool that runs entirely on your machine. It transcribes audio files, identifies who said what, and optionally summarizes the result using a local Ollama model. No cloud APIs, no gated models, no tokens. The CLI command is `vox`.

It is NOT a real-time transcription tool, not a GUI app, and not a cloud service wrapper.

## Quick Reference

| Task | Command |
|---|---|
| Test | `uv run pytest --tb=short` |
| Lint | `uv run ruff check src/ tests/` |
| Format | `uv run ruff format src/ tests/` |
| Type check | `uv run ty check src/ tests/` |

## Intended Workflow

```
vox meeting.m4a                    # transcribe with speaker labels
vox rename meeting.md              # interactively assign real names
vox summarize meeting.md           # produce structured meeting notes
```

## Design Decisions

| Decision | Choice | Why |
|----------|--------|-----|
| Transcription engine | faster-whisper (CTranslate2) | Best local accuracy, good Python API |
| Diarization | speechbrain | Fully open models, no HuggingFace token required |
| Summarization | Ollama (local) | Keeps everything local, user controls model choice |
| CLI framework | typer + rich + questionary | Clean CLI with interactive prompts where useful |
| Audio handling | torchaudio | Handles format conversion (m4a, mp3, wav) reliably |
| Output format | Markdown only | Simple, readable, feeds into downstream tools |
| Prompt templates | `.md` files with `{transcript}` placeholder | Easy to customize, version-controllable |

## Python Standards

### Tooling

| Tool | Purpose |
|---|---|
| uv | Package management |
| hatchling | Build backend |
| ruff | Formatting and linting |
| ty | Type checking |
| pytest | Testing |
| pre-commit | Git hooks (conventional commits, ruff, ty) |
| release-please | Automated versioning and releases |
| Renovate | Automated dependency updates |

### Preferred Libraries

| Need | Reach for |
|---|---|
| Backend / API | FastAPI |
| Structured data / config | Pydantic |
| CLI | typer |
| AI / agents | PydanticAI |
| Test fixtures | Polyfactory |

### Patterns

- **Logging:** `%s` formatting (`logger.info("msg %s", var)`), not f-strings
- **Pydantic** for config and structured data, **dataclasses** for simple internal value objects
- **src-layout:** all source code under `src/vox_machina/`
- Functional style preferred (pure functions, composition)
- Type hints on all public functions
- Group imports from the same module on one line
- No em dashes in any text output or documentation

## Project Layout

```
vox-machina/
├── src/vox_machina/
│   ├── cli.py              # typer app: main, rename, summarize commands
│   ├── models.py           # pydantic models: TranscriptSegment, SpeakerSegment, MergedSegment
│   ├── transcribe.py       # faster-whisper wrapper
│   ├── diarize.py          # speechbrain diarization
│   ├── merge.py            # align transcription with speaker segments
│   ├── format.py           # render to markdown
│   ├── rename.py           # speaker label extraction and replacement
│   ├── summarize.py        # Ollama summarization + context window check
│   ├── banner.py           # ASCII art banner
│   └── prompts/
│       ├── meeting_notes.md
│       ├── standup.md
│       └── interview.md
└── tests/
    ├── test_models.py
    ├── test_merge.py
    ├── test_format.py
    ├── test_rename.py
    ├── test_summarize.py
    └── test_cli.py
```

## Related Documents

- [Roadmap](./notes/roadmap.md) - implementation plans for v0.1.0 through v0.7.0
