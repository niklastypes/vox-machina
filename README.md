# vox-machina

> 🦻 Local voice transcription with speaker diarization and LLM-powered summarization

## Setup

```bash
uv sync --all-extras
uv run pre-commit install
```

Then enable release-please: go to **Settings → Actions → General → Workflow permissions** and check **Allow GitHub Actions to create and approve pull requests**.

## Development

| Task | Command |
|---|---|
| Test | `uv run pytest --tb=short` |
| Lint | `uv run ruff check src/ tests/` |
| Format | `uv run ruff format src/ tests/` |
| Type check | `uv run ty check src/ tests/` |

## License

MIT

---

🪵 Kindled with [Kindling](https://github.com/niklastypes/kindling)
