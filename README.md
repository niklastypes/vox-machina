# 🦻 Vox Machina

Local voice transcription with speaker diarization and LLM-powered summarization.

Drop in audio, get structured meeting notes. Runs entirely on your machine with no cloud APIs, no gated models, no tokens.

## How It Works

```
vox meeting.m4a                    # transcribe to timestamped markdown
```

## Tech Stack

Python 3.13, faster-whisper, typer, Pydantic, rich

## Roadmap

| Stage | Version | What it delivers |
|-------|---------|-----------------|
| Skateboard | v0.1.0 | `vox file.m4a` produces timestamped transcript |
| Scooter | v0.2.0 | Adds speaker diarization (SPEAKER_00, SPEAKER_01, ...) |
| Bicycle | v0.3.0 | `vox rename` for interactive speaker label replacement |
| Motorcycle | v0.4.0 | `vox summarize` via local Ollama with prompt templates |
| Polish | v0.5.0 | ASCII banner, polished rich UX throughout |
| Summaries+ | v0.6.0 | Multiple prompt templates + chunked summarization for long recordings |
| Obsidian | v0.7.0 | Obsidian-ready output with frontmatter, tags, wikilinks |

## Prerequisites

- **ffmpeg** is required for decoding audio formats (m4a, aac, mp3, etc.): `brew install ffmpeg`

## Setup

```bash
uv sync --all-extras
uv run pre-commit install
```

Then enable release-please: go to **Settings > Actions > General > Workflow permissions** and check **Allow GitHub Actions to create and approve pull requests**.

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
