from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from vox_machina.summarize import list_builtin_prompts, render_prompt


def test_render_default_prompt() -> None:
    result = render_prompt(None, "Hello world")
    assert "Hello world" in result
    assert "Key Topics" in result


def test_render_builtin_standup() -> None:
    result = render_prompt("standup", "Some standup text")
    assert "Some standup text" in result
    assert "What they did" in result


def test_render_builtin_retro() -> None:
    result = render_prompt("retro", "My retro thoughts")
    assert "My retro thoughts" in result
    assert "Loose threads" in result


def test_render_builtin_interview() -> None:
    result = render_prompt("interview", "Interview content")
    assert "Interview content" in result
    assert "Notable Quotes" in result


def test_render_shares_base_rules() -> None:
    """All built-in templates should include the shared base rules."""
    for name in list_builtin_prompts():
        result = render_prompt(name, "test")
        assert "Do not add commentary" in result
        assert "same language as the transcript" in result


def test_render_custom_file(tmp_path: Path) -> None:
    custom = tmp_path / "custom.md"
    custom.write_text("Summarize this: {transcript}")
    result = render_prompt(str(custom), "Hello")
    assert result == "Summarize this: Hello"


def test_render_nonexistent_raises() -> None:
    with pytest.raises(FileNotFoundError, match="not found"):
        render_prompt("nonexistent_prompt", "text")


def test_list_builtin_prompts() -> None:
    prompts = list_builtin_prompts()
    assert "meeting_notes" in prompts
    assert "standup" in prompts
    assert "interview" in prompts
    assert "retro" in prompts
    assert "base" not in prompts


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
