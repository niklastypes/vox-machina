import re


def extract_speakers(transcript: str) -> list[str]:
    pattern = re.compile(r"\*\*(SPEAKER_\d+)\*\*")
    seen: set[str] = set()
    ordered: list[str] = []
    for match in pattern.finditer(transcript):
        speaker = match.group(1)
        if speaker not in seen:
            seen.add(speaker)
            ordered.append(speaker)
    return ordered


def extract_first_quotes(transcript: str, speakers: list[str]) -> dict[str, str]:
    quotes: dict[str, str] = {}
    for speaker in speakers:
        pattern = re.compile(rf"\*\*{re.escape(speaker)}\*\*\s*\([^)]+\)\n(.+)")
        match = pattern.search(transcript)
        if match:
            quotes[speaker] = match.group(1).strip()
    return quotes


def rename_speakers(transcript: str, mapping: dict[str, str]) -> str:
    result = transcript
    for old_name, new_name in mapping.items():
        result = result.replace(f"**{old_name}**", f"**{new_name}**")
    return result


def parse_speaker_mapping(raw: str) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for pair in raw.split(","):
        key, value = pair.strip().split("=", 1)
        mapping[key.strip()] = value.strip()
    return mapping
