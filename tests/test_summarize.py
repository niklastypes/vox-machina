from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from vox_machina.summarize import (
    build_prompt,
    list_builtin_prompts,
    load_prompt_template,
)


def test_load_default_prompt_template() -> None:
    template = load_prompt_template()
    assert "{transcript}" in template
    assert "Key Topics" in template


def test_load_builtin_by_name() -> None:
    template = load_prompt_template("standup")
    assert "{transcript}" in template
    assert "What they did" in template


def test_load_builtin_retro() -> None:
    template = load_prompt_template("retro")
    assert "{transcript}" in template
    assert "Loose threads" in template


def test_load_builtin_interview() -> None:
    template = load_prompt_template("interview")
    assert "{transcript}" in template
    assert "Notable Quotes" in template


def test_load_custom_prompt_by_path(tmp_path: Path) -> None:
    custom = tmp_path / "custom.md"
    custom.write_text("Summarize this: {transcript}")
    template = load_prompt_template(str(custom))
    assert template == "Summarize this: {transcript}"


def test_load_nonexistent_prompt_raises() -> None:
    with pytest.raises(FileNotFoundError, match="not found"):
        load_prompt_template("nonexistent_prompt")


def test_list_builtin_prompts() -> None:
    prompts = list_builtin_prompts()
    assert "meeting_notes" in prompts
    assert "standup" in prompts
    assert "interview" in prompts
    assert "retro" in prompts


def test_build_prompt_injects_transcript() -> None:
    template = "Summary of: {transcript}"
    result = build_prompt(template, "Hello world conversation")
    assert result == "Summary of: Hello world conversation"


@patch("vox_machina.summarize.verify_model_available")
@patch("vox_machina.summarize.ollama")
def test_summarize_transcript_calls_ollama(
    mock_ollama: MagicMock,
    _mock_verify: MagicMock,
) -> None:
    from vox_machina.summarize import summarize_transcript

    mock_ollama.chat.return_value.message.content = "## Summary\nStuff happened"

    result = summarize_transcript("Some transcript text", model="qwen3.5:9b")

    mock_ollama.chat.assert_called_once()
    call_kwargs = mock_ollama.chat.call_args
    assert call_kwargs.kwargs["model"] == "qwen3.5:9b"
    assert "Some transcript text" in call_kwargs.kwargs["messages"][0]["content"]
    assert "num_ctx" in call_kwargs.kwargs["options"]
    assert result == "## Summary\nStuff happened"


@patch("vox_machina.summarize.verify_model_available")
@patch("vox_machina.summarize.ollama")
def test_summarize_transcript_with_named_prompt(
    mock_ollama: MagicMock,
    _mock_verify: MagicMock,
) -> None:
    from vox_machina.summarize import summarize_transcript

    mock_ollama.chat.return_value.message.content = "Retro summary"

    result = summarize_transcript(
        "Transcript text", model="qwen3.5:9b", prompt_name="retro"
    )

    call_content = mock_ollama.chat.call_args.kwargs["messages"][0]["content"]
    assert "Transcript text" in call_content
    assert "Loose threads" in call_content
    assert result == "Retro summary"
