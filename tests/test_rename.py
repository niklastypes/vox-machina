import pytest

from vox_machina.rename import (
    extract_quotes,
    extract_speakers,
    parse_speaker_mapping,
    rename_speakers,
)


def test_extract_speakers_finds_all_speakers() -> None:
    transcript = (
        "**SPEAKER_00** (00:00:01)\nHello\n\n"
        "**SPEAKER_01** (00:00:04)\nHi there\n\n"
        "**SPEAKER_00** (00:00:08)\nHow are you?\n"
    )
    speakers = extract_speakers(transcript)
    assert speakers == ["SPEAKER_00", "SPEAKER_01"]


def test_extract_speakers_returns_empty_for_no_speakers() -> None:
    transcript = "Just some text without speakers."
    assert extract_speakers(transcript) == []


def test_rename_speakers_replaces_all_occurrences() -> None:
    transcript = (
        "**SPEAKER_00** (00:00:01)\nHello\n\n"
        "**SPEAKER_01** (00:00:04)\nHi\n\n"
        "**SPEAKER_00** (00:00:08)\nBye\n"
    )
    mapping = {"SPEAKER_00": "Alice", "SPEAKER_01": "Bob"}
    result = rename_speakers(transcript, mapping)

    assert "**Alice**" in result
    assert "**Bob**" in result
    assert "SPEAKER_00" not in result
    assert "SPEAKER_01" not in result


def test_rename_speakers_preserves_unmapped_speakers() -> None:
    transcript = "**SPEAKER_00** (00:00:01)\nHello\n\n**SPEAKER_01** (00:00:04)\nHi\n"
    mapping = {"SPEAKER_00": "Alice"}
    result = rename_speakers(transcript, mapping)

    assert "**Alice**" in result
    assert "**SPEAKER_01**" in result


def test_parse_speaker_mapping() -> None:
    raw = "SPEAKER_00=Alice,SPEAKER_01=Bob"
    result = parse_speaker_mapping(raw)
    assert result == {"SPEAKER_00": "Alice", "SPEAKER_01": "Bob"}


def test_extract_quotes_returns_all_quotes_per_speaker() -> None:
    transcript = (
        "**SPEAKER_00** (00:00:01)\nFirst thing\n\n"
        "**SPEAKER_01** (00:00:04)\nAnother thing\n\n"
        "**SPEAKER_00** (00:00:08)\nSecond thing\n"
    )
    speakers = extract_speakers(transcript)
    quotes = extract_quotes(transcript, speakers)
    assert quotes["SPEAKER_00"] == ["First thing", "Second thing"]
    assert quotes["SPEAKER_01"] == ["Another thing"]


def test_parse_speaker_mapping_rejects_malformed_input() -> None:
    with pytest.raises(ValueError, match="Invalid speaker mapping"):
        parse_speaker_mapping("SPEAKER_00")
