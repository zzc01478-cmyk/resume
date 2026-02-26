---
name: video-audio-processor
description: Comprehensive video processing and audio transcription tool. Extract frames, convert formats, extract audio, and transcribe speech using Whisper.
homepage: https://ffmpeg.org
metadata: {
  "clawdbot": {
    "emoji": "🎬",
    "requires": {
      "bins": ["ffmpeg", "python3"]
    },
    "install": [
      {
        "id": "ffmpeg",
        "kind": "apt",
        "package": "ffmpeg",
        "bins": ["ffmpeg"],
        "label": "Install ffmpeg"
      },
      {
        "id": "whisper",
        "kind": "pip",
        "package": "openai-whisper",
        "label": "Install Whisper (Python)"
      },
      {
        "id": "pydub",
        "kind": "pip", 
        "package": "pydub",
        "label": "Install pydub for audio processing"
      }
    ]
  }
}
---

# Video & Audio Processor

A comprehensive tool for video processing and audio transcription. Combines ffmpeg for video/audio manipulation and OpenAI Whisper for speech-to-text transcription.

## Features

### Video Processing
- Extract frames at specific times or intervals
- Convert video formats
- Extract audio from video
- Generate thumbnails and previews
- Get video metadata and information

### Audio Processing  
- Extract audio from video files
- Convert audio formats
- Split audio by silence or duration
- Normalize audio volume

### Speech-to-Text
- Transcribe audio using Whisper (local, no API needed)
- Multiple model sizes (tiny, base, small, medium, large)
- Support for multiple languages
- Timestamp generation
- Output in TXT, JSON, SRT, VTT formats

## Quick Start

### 1. Install Dependencies
```bash
# Install ffmpeg
apt-get install ffmpeg

# Install Python dependencies
pip install openai-whisper pydub
```

### 2. Extract Audio from Video
```bash
{baseDir}/scripts/extract_audio.sh video.mp4 --output audio.wav
```

### 3. Transcribe Audio
```bash
{baseDir}/scripts/transcribe.sh audio.wav --model base --language en
```

### 4. Extract Video Frames
```bash
{baseDir}/scripts/extract_frames.sh video.mp4 --interval 10 --output frames/
```

## Usage Examples

### Get Video Information
```bash
{baseDir}/scripts/video_info.sh video.mp4
```

### Extract Audio and Transcribe in One Command
```bash
{baseDir}/scripts/video_to_text.sh video.mp4 --model small --output transcript.txt
```

### Create Video Preview (GIF)
```bash
{baseDir}/scripts/create_preview.sh video.mp4 --duration 5 --output preview.gif
```

### Batch Process Multiple Videos
```bash
{baseDir}/scripts/batch_process.sh *.mp4 --transcribe --output transcripts/
```

## Configuration

### Whisper Model Selection
- `tiny`: Fastest, lowest accuracy
- `base`: Good balance (default)
- `small`: Better accuracy
- `medium`: High accuracy
- `large`: Best accuracy, slowest

### Output Formats
- `txt`: Plain text
- `json`: JSON with timestamps and confidence
- `srt`: SubRip subtitles
- `vtt`: WebVTT subtitles

## Performance Tips

1. **For short videos**: Use `tiny` or `base` model
2. **For high accuracy**: Use `small` or `medium` model  
3. **For multiple files**: Process in parallel if possible
4. **For large videos**: Extract audio first, then transcribe

## Notes

- First run will download the Whisper model (100MB-3GB depending on model)
- GPU acceleration available if CUDA is installed
- Supports most video/audio formats via ffmpeg
- All processing happens locally, no data sent to external servers

## Troubleshooting

### Common Issues

1. **ffmpeg not found**: Install ffmpeg via package manager
2. **Whisper download fails**: Check internet connection, try smaller model
3. **Memory issues**: Use smaller model or split audio
4. **Format not supported**: Convert to WAV/MP3 first

### Debug Mode
Add `--verbose` flag to any script to see detailed output.

## Related Skills

- `video-frames`: Basic frame extraction
- `doubao-open-tts`: Text-to-speech (opposite direction)
- `audio-tools`: Additional audio processing utilities

## License

MIT License. Uses ffmpeg (LGPL/GPL) and Whisper (MIT).