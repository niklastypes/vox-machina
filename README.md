# 🦻 Vox Machina

Local voice transcription with speaker diarization and LLM-powered summarization.

Drop in audio, get structured meeting notes. Runs entirely on your machine, no cloud APIs at runtime.

## How It Works

Two CLI entry points, split by domain:

### `vox` - voice and audio

| Command | What it does |
|---------|-------------|
| `vox transcribe meeting.m4a` | Transcribe with speaker diarization |
| `vox transcribe meeting.m4a --language de` | Force language (auto-detects if omitted) |
| `vox config` | Configure default models |
| `vox prepare` | Download all required models |

### `machina` - text processing and AI

| Command | What it does |
|---------|-------------|
| `machina label meeting.md` | Interactively assign real names to speakers |
| `machina summarize meeting.md` | Summarize (picks prompt interactively) |
| `machina summarize meeting.md --prompt retro` | Summarize with a specific prompt template |

## Tech Stack

Python 3.13, faster-whisper, pyannote.audio, Ollama, typer, Pydantic, rich, questionary, Jinja2

## Prerequisites

- **ffmpeg** for decoding audio formats (m4a, aac, mp3, etc.): `brew install ffmpeg`
- **Ollama** for transcript summarization: [ollama.com](https://ollama.com), then pull a model (see below)

### Choosing an Ollama model

Summarization quality scales with model size. Pick a model that fits your available RAM (total RAM minus ~4GB for OS/apps). Rule of thumb: ~0.6-0.7GB per billion parameters at Q4 quantization.

| Available RAM | Model size | Examples |
|--------------|------------|----------|
| ~4-5GB (8GB machines) | 3-4B | `qwen3.5:4b`, `gemma3:4b`, `phi4-mini` |
| ~12GB (16GB machines) | 7-9B | `qwen3.5:9b` (default), `gemma3:12b`, `mistral:7b` |
| ~44GB (48GB+ machines) | 27-35B | `qwen3.5:27b`, `gemma4:27b`, `mistral-small:24b` |

```bash
ollama pull qwen3.5:9b    # or whichever model fits your machine
```

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

## Responsible Use

> [!IMPORTANT]
> vox-machina processes audio recordings that may contain personal conversations. Please make sure you have the **consent of all recorded parties** before transcribing. Many jurisdictions require explicit consent for recording and transcribing conversations. The speaker diarization model ([pyannote](https://huggingface.co/pyannote/speaker-diarization-community-1)) also requires users to respect its license terms, which include responsible use of speaker identification.

## License

MIT

---

🪵 Kindled with [Kindling](https://github.com/niklastypes/kindling)
