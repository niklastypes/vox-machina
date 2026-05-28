import json
from pathlib import Path

from pydantic import BaseModel


CONFIG_DIR = Path.home() / ".config" / "vox-machina"
CONFIG_PATH = CONFIG_DIR / "config.json"

DEFAULT_WHISPER_MODEL = "large-v3"
DEFAULT_OLLAMA_MODEL = "qwen3.5:9b"


class VoxConfig(BaseModel):
    whisper_model: str = DEFAULT_WHISPER_MODEL
    ollama_model: str = DEFAULT_OLLAMA_MODEL
    obsidian_mode: bool = False


def load_config() -> VoxConfig:
    if CONFIG_PATH.exists():
        data = json.loads(CONFIG_PATH.read_text())
        return VoxConfig(**data)
    return VoxConfig()


def save_config(config: VoxConfig) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config.model_dump(), indent=2) + "\n")


def config_exists() -> bool:
    return CONFIG_PATH.exists()
