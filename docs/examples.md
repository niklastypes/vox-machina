# Usage Examples

## Basic workflow

Record a meeting, get structured notes:

```bash
vox transcribe meeting.m4a
machina label meeting.md
machina summarize meeting.md
```

## Personal retrospective

Record yourself talking about what's on your mind, get a structured summary:

```bash
vox transcribe retro.m4a --language de
machina summarize retro.md --prompt retro
```

## Summarize a YouTube video

vox-machina focuses on local audio processing, but you can easily combine it with [yt-dlp](https://github.com/yt-dlp/yt-dlp) to summarize YouTube videos:

```bash
# Extract audio from a YouTube video
yt-dlp -x --audio-format wav -o talk.wav "https://youtube.com/watch?v=..."

# Transcribe and summarize
vox transcribe talk.wav
machina summarize talk.md --prompt talk
```

For videos with existing subtitles, you can skip transcription entirely and go straight to summarization:

```bash
# Download subtitles as text
yt-dlp --write-auto-sub --sub-lang en --skip-download -o talk "https://youtube.com/watch?v=..."

# Convert to plain text, save as .md, then summarize
machina summarize talk.md --prompt talk
```

## Non-interactive mode (scripting)

All interactive prompts can be bypassed with flags:

```bash
# Skip speaker labeling questionnaire
machina label meeting.md --speakers "SPEAKER_00=Alice,SPEAKER_01=Bob"

# Skip prompt template questionnaire
machina summarize meeting.md --prompt meeting_notes

# Skip language detection
vox transcribe meeting.m4a --language en
```

## Clean transcript (no timestamps)

For downstream processing where timestamps add noise:

```bash
vox transcribe meeting.m4a --no-timestamps
```

## Custom prompt template

Create your own `.md` file with a `{transcript}` placeholder:

```markdown
Summarize this in three bullet points:

{transcript}
```

Then use it:

```bash
machina summarize meeting.md --prompt /path/to/custom.md
```
