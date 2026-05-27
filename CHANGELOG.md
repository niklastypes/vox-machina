# Changelog

## [0.5.0](https://github.com/niklastypes/vox-machina/compare/v0.4.0...v0.5.0) (2026-05-27)


### Features

* add Ollama-based transcript summarization with prompt templates ([3a161d6](https://github.com/niklastypes/vox-machina/commit/3a161d69a99b53ff675b16422db557012d42a817))
* add summarize command to CLI ([aa7eea6](https://github.com/niklastypes/vox-machina/commit/aa7eea60a498aeb8e87a24f7e266574cedc554ba))
* default summarization model to qwen3.5 ([3a361b7](https://github.com/niklastypes/vox-machina/commit/3a361b7352024020df24676bcf36c9051ed9b0e4))
* improve summarization prompt for raw transcriptions ([0f5fbd2](https://github.com/niklastypes/vox-machina/commit/0f5fbd2cb0ccdd7e07fd483596d73828e595ee71))


### Documentation

* update README.md, CLAUDE.md and roadmap for v0.4.0 ([a9a53ae](https://github.com/niklastypes/vox-machina/commit/a9a53ae5445d131a8accef9183573f153ee2c00c))

## [0.4.0](https://github.com/niklastypes/vox-machina/compare/v0.3.0...v0.4.0) (2026-05-27)


### Features

* add interactive speaker rename command ([fb89298](https://github.com/niklastypes/vox-machina/commit/fb89298acba6b7e830c90b4aedf7340c054d392a))
* add speaker extraction, renaming, and quote preview ([e8db734](https://github.com/niklastypes/vox-machina/commit/e8db734aa55870f3dce7610018315c4c694e2e31))
* extract all quotes per speaker for richer rename previews ([cc21a75](https://github.com/niklastypes/vox-machina/commit/cc21a755bf39112e590a41ba7e2a2fa9d5c3b971))
* improved interactive rename with show-more option ([c402c8b](https://github.com/niklastypes/vox-machina/commit/c402c8bd779108aa223dfb3abb1f5d0a4d26d077))
* validate .md file extension in rename command ([36350f1](https://github.com/niklastypes/vox-machina/commit/36350f1b86b03600a652c0740a906a334c507791))


### Bug Fixes

* handle Ctrl+C gracefully during interactive rename ([e9c2ee1](https://github.com/niklastypes/vox-machina/commit/e9c2ee15e736942d7dac02a0cb5aaa491d2259fc))
* validate speaker mapping format in --speakers flag ([cbd2d59](https://github.com/niklastypes/vox-machina/commit/cbd2d591de137a0faae5c13024b96cfb00d4e99e))


### Documentation

* update README.md, CLAUDE.md and roadmap for v0.3.0 ([b114a90](https://github.com/niklastypes/vox-machina/commit/b114a901419fed1093128719fcc64284b9462f35))

## [0.3.0](https://github.com/niklastypes/vox-machina/compare/v0.2.0...v0.3.0) (2026-05-26)


### Features

* add merge logic to align transcripts with speaker segments ([64cac45](https://github.com/niklastypes/vox-machina/commit/64cac4567fa9913af823c5e18b36b12a78177616))
* add pyannote speaker diarization module ([dfc83f6](https://github.com/niklastypes/vox-machina/commit/dfc83f6c1323e6971324f1a91ed19886b63e0aa0))
* add speaker-aware markdown formatting with grouping ([2f8ab29](https://github.com/niklastypes/vox-machina/commit/2f8ab298090669ed761a8a451da89ca565042a5c))
* add SpeakerSegment and MergedSegment models ([87ac440](https://github.com/niklastypes/vox-machina/commit/87ac4407db60cc453b95b579697e9312ff3705f7))
* integrate speaker diarization into transcription pipeline ([d89d5a6](https://github.com/niklastypes/vox-machina/commit/d89d5a6809d91bcea56db5724b350c770f6155f8))


### Bug Fixes

* use per-segment timestamps for single-speaker transcripts ([ac773f5](https://github.com/niklastypes/vox-machina/commit/ac773f5ec0a28935e6166b169a640750c24aa93f))


### Documentation

* add HuggingFace setup instructions for diarization model ([3c4c1b1](https://github.com/niklastypes/vox-machina/commit/3c4c1b111255c1d01078c3ccd9e68ef32e08857b))
* update README.md, CLAUDE.md and roadmap for v0.2.0 ([9b537fc](https://github.com/niklastypes/vox-machina/commit/9b537fc01e4eace40d1cd85230aa68d5b5383dad))

## [0.2.0](https://github.com/niklastypes/vox-machina/compare/v0.1.0...v0.2.0) (2026-05-26)


### Features

* add CLI with transcribe command ([4b4d89b](https://github.com/niklastypes/vox-machina/commit/4b4d89bf9ed81d0dc934ec7583f9e9cc86b6b0f1))
* add faster-whisper transcription module ([21b710f](https://github.com/niklastypes/vox-machina/commit/21b710f96b6e29f5789e29344c20184f6e3fcdc1))
* add markdown transcript formatter with timestamps ([b5c16b5](https://github.com/niklastypes/vox-machina/commit/b5c16b50b1c819f45c35de11463f78c8dd8b7c18))
* add TranscriptSegment pydantic model ([8b0f25d](https://github.com/niklastypes/vox-machina/commit/8b0f25dc85f13380023330569ce320cfa1feaed7))


### Bug Fixes

* convert non-wav audio via ffmpeg before transcription ([2b4dac8](https://github.com/niklastypes/vox-machina/commit/2b4dac86e7e67e19344080b8c2e9bbd5019aa59d))


### Documentation

* add roadmap ([0c9601e](https://github.com/niklastypes/vox-machina/commit/0c9601e55c148bf93752bdb6a1607c3278e308db))
* update README.md & CLAUDE.md ([f247956](https://github.com/niklastypes/vox-machina/commit/f247956872c884418cf301121c195f496676a39d))
* update README.md, CLAUDE.md & notes/roadmap.md ([dcc5b05](https://github.com/niklastypes/vox-machina/commit/dcc5b055847ea6987338553dbad20e07f907c172))
