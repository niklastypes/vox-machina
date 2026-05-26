# 🦻 Vox Machina

Local voice transcription with speaker diarization and LLM-powered summarization.

Drop in audio, get structured meeting notes. Runs entirely on your machine, no cloud APIs at runtime.

## How It Works

```
vox meeting.m4a                    # transcribe with speaker labels
```

## Tech Stack

Python 3.13, faster-whisper, pyannote.audio, typer, Pydantic, rich

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

### Speaker diarization model

Speaker diarization uses [pyannote/speaker-diarization-community-1](https://huggingface.co/pyannote/speaker-diarization-community-1) (CC-BY-4.0). The model runs fully locally, but requires a one-time HuggingFace login to download:

1. Create a free account at [huggingface.co](https://huggingface.co/join)
2. Accept the model terms at [pyannote/speaker-diarization-community-1](https://huggingface.co/pyannote/speaker-diarization-community-1)
3. Create a **Read** access token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
4. Log in locally:

```bash
uv run hf auth login
```

If you skip this step, transcription still works but without speaker labels.

### Release-please

To enable automated releases: go to **Settings > Actions > General > Workflow permissions** and check **Allow GitHub Actions to create and approve pull requests**.

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
