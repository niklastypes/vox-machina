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


def extract_quotes(transcript: str, speakers: list[str]) -> dict[str, list[str]]:
    quotes: dict[str, list[str]] = {s: [] for s in speakers}
    pattern = re.compile(r"\*\*(\w+)\*\*\s*\([^)]+\)\n(.+)")
    for match in pattern.finditer(transcript):
        speaker, text = match.group(1), match.group(2).strip()
        if speaker in quotes:
            quotes[speaker].append(text)
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
