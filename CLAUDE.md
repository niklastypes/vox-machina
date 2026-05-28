# vox-machina

🦻 Local voice transcription with speaker diarization and LLM-powered summarization

## Core Identity

vox-machina is a focused pipeline tool: audio in, structured markdown artifacts out. Two entry points: `vox` (audio + project config) and `machina` (text processing). Runs entirely on your machine, no cloud APIs at runtime.

## Quick Reference

| Task | Command |
|---|---|
| Test | `uv run pytest --tb=short` |
| Lint | `uv run ruff check src/ tests/` |
| Format | `uv run ruff format src/ tests/` |
| Type check | `uv run ty check src/ tests/` |

## Current Workflow

```
vox transcribe meeting.m4a                          # transcribe with speaker labels
vox transcribe meeting.m4a --language de            # force language detection
vox transcribe meeting.m4a --no-timestamps          # omit timestamps
vox config                                          # configure default models (incl. Obsidian mode)
vox prepare                                         # download all required models

machina label meeting.md                            # interactively assign real names
machina summarize meeting.md                        # summarize (picks prompt + detail interactively)
machina summarize meeting.md --prompt retro         # use a specific prompt template
machina summarize meeting.md --detail detailed      # thorough summary
```

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
src/vox_machina/
├── vox_app.py          # vox CLI: transcribe, config, prepare
├── machina_app.py      # machina CLI: label, summarize
├── cli.py              # shared CLI helpers (config questionnaire, prompts)
├── config.py           # persistent user config (~/.config/vox-machina/)
├── prepare.py          # model download orchestration
├── banner.py           # ASCII art banner
├── models.py           # pydantic models: TranscriptSegment, SpeakerSegment, MergedSegment
├── transcribe.py       # faster-whisper wrapper (ffmpeg conversion for non-wav)
├── diarize.py          # pyannote speaker diarization
├── merge.py            # align transcript segments with speaker segments
├── format.py           # render merged segments to markdown with speaker labels
├── label.py            # speaker label extraction and assignment
├── summarize.py        # Ollama summarization with Jinja2 prompt templates
├── obsidian.py         # YAML frontmatter generation for Obsidian
└── prompts/
    ├── base.md.j2          # shared rules (Jinja2 base template)
    ├── meeting_notes.md.j2 # meeting summary format
    ├── standup.md.j2       # standup/status update format
    ├── interview.md.j2     # interview summary format
    ├── retro.md.j2         # personal retrospective format
    └── talk.md.j2          # technical talk/presentation format

tests/
├── test_cli.py
├── test_config.py
├── test_models.py
├── test_merge.py
├── test_format.py
├── test_label.py
├── test_obsidian.py
└── test_summarize.py
```

## Related Documents

- [Architecture](./docs/architecture.md) - pipeline stages, CLI split, data models, design decisions
- [Examples](./docs/examples.md) - usage examples including YouTube workflow
- [Roadmap](./notes/roadmap.md) - implementation plans for v0.10.0 through v0.15.0
