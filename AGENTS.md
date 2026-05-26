# vox-machina

🦻 Local voice transcription with speaker diarization and LLM-powered summarization

## Quick Reference

| Task | Command |
|---|---|
| Test | `uv run pytest --tb=short` |
| Lint | `uv run ruff check src/ tests/` |
| Format | `uv run ruff format src/ tests/` |
| Type check | `uv run ty check src/ tests/` |

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

## Project Layout

```
src/vox_machina/
tests/
```
