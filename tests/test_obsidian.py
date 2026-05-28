from vox_machina.obsidian import summary_frontmatter, transcript_frontmatter


def test_transcript_frontmatter_basic() -> None:
    result = transcript_frontmatter(
        source_filename="meeting.m4a",
        duration="00:11:28",
    )

    assert "type: transcript" in result
    assert "source: meeting.m4a" in result
    assert 'duration: "00:11:28"' in result
    assert "- transcript" in result
    assert result.startswith("---")
    assert result.endswith("---")


def test_transcript_frontmatter_with_models_and_speakers() -> None:
    result = transcript_frontmatter(
        source_filename="meeting.m4a",
        duration="00:11:28",
        whisper_model="small",
        diarization_model="pyannote/speaker-diarization-community-1",
        speakers=["Alice", "Bob"],
    )

    assert "whisper_model: small" in result
    assert "diarization_model: pyannote/speaker-diarization-community-1" in result
    assert "- Alice" in result
    assert "- Bob" in result


def test_summary_frontmatter_basic() -> None:
    result = summary_frontmatter(
        source_filename="meeting.md",
        model="qwen3.5:9b",
        prompt_name="meeting_notes",
    )

    assert "type: summary" in result
    assert "source: meeting.md" in result
    assert "model: qwen3.5:9b" in result
    assert "prompt: meeting_notes" in result
    assert "- summary" in result
    assert "- meeting-notes" in result


def test_summary_frontmatter_with_upstream_models() -> None:
    result = summary_frontmatter(
        source_filename="meeting.md",
        model="qwen3.5:9b",
        prompt_name="meeting_notes",
        whisper_model="small",
        diarization_model="pyannote/speaker-diarization-community-1",
    )

    assert "whisper_model: small" in result
    assert "diarization_model: pyannote/speaker-diarization-community-1" in result


def test_summary_frontmatter_retro_tags() -> None:
    result = summary_frontmatter(
        source_filename="retro.md",
        model="qwen3.5:9b",
        prompt_name="retro",
    )

    assert "- summary" in result
    assert "- retro" in result
