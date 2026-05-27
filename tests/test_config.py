import json
from unittest.mock import patch

from vox_machina.config import VoxConfig, load_config, save_config


def test_default_config() -> None:
    config = VoxConfig()
    assert config.whisper_model == "large-v3"
    assert config.ollama_model == "qwen3.5:9b"


def test_save_and_load_config(tmp_path):
    config_path = tmp_path / "config.json"
    config = VoxConfig(whisper_model="small", ollama_model="gemma4:e4b")

    with (
        patch("vox_machina.config.CONFIG_PATH", config_path),
        patch("vox_machina.config.CONFIG_DIR", tmp_path),
    ):
        save_config(config)

        assert config_path.exists()
        data = json.loads(config_path.read_text())
        assert data["whisper_model"] == "small"
        assert data["ollama_model"] == "gemma4:e4b"

        loaded = load_config()
        assert loaded.whisper_model == "small"
        assert loaded.ollama_model == "gemma4:e4b"


def test_load_config_returns_defaults_when_no_file(tmp_path):
    config_path = tmp_path / "nonexistent.json"
    with patch("vox_machina.config.CONFIG_PATH", config_path):
        config = load_config()
        assert config.whisper_model == "large-v3"
        assert config.ollama_model == "qwen3.5:9b"
