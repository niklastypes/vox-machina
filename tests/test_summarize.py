from pathlib import Path
from unittest.mock import MagicMock, patch

from vox_machina.summarize import build_prompt, load_prompt_template


def test_load_default_prompt_template() -> None:
    template = load_prompt_template()
    assert "{transcript}" in template
    assert "Key Topics" in template


def test_load_custom_prompt_template(tmp_path: Path) -> None:
    custom = tmp_path / "custom.md"
    custom.write_text("Summarize this: {transcript}")
    template = load_prompt_template(str(custom))
    assert template == "Summarize this: {transcript}"


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
def test_summarize_transcript_with_custom_prompt(
    mock_ollama: MagicMock,
    _mock_verify: MagicMock,
    tmp_path: Path,
) -> None:
    from vox_machina.summarize import summarize_transcript

    mock_ollama.chat.return_value.message.content = "Custom summary"
    custom = tmp_path / "custom.md"
    custom.write_text("Just summarize: {transcript}")

    result = summarize_transcript(
        "Transcript text", model="qwen3.5:9b", prompt_path=str(custom)
    )

    call_content = mock_ollama.chat.call_args.kwargs["messages"][0]["content"]
    assert call_content == "Just summarize: Transcript text"
    assert result == "Custom summary"
