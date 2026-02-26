# Video & Audio Processor Skill

A comprehensive OpenClaw skill for video processing and audio transcription. Combines ffmpeg for video/audio manipulation and OpenAI Whisper for speech-to-text transcription.

## 🎯 Features

### Video Processing
- 📊 Extract video metadata and information
- 🖼️ Extract frames at specific times or intervals  
- 🔄 Convert video formats
- 🔊 Extract audio from video files
- 🎞️ Generate thumbnails and previews

### Audio Processing
- 🎵 Extract audio from video files
- 🔧 Convert audio formats (MP3, WAV, FLAC)
- ✂️ Split audio by silence or duration
- 🔊 Normalize audio volume

### Speech-to-Text (ASR)
- 🗣️ Transcribe audio using OpenAI Whisper (local, no API needed)
- 🌐 Multiple model sizes (tiny, base, small, medium, large)
- 🈶 Support for 99+ languages
- ⏱️ Timestamp generation
- 📝 Output in TXT, JSON, SRT, VTT formats

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# Navigate to skill directory
cd /root/.openclaw/workspace/skills/video-audio-processor

# Run installation script
./scripts/install_deps.sh
```

### 2. Test Installation
```bash
# Run tests to verify everything works
./scripts/test_installation.sh
```

### 3. Basic Usage Examples

#### Get video information:
```bash
./scripts/video_info.sh /path/to/video.mp4
```

#### Extract audio from video:
```bash
./scripts/extract_audio.sh /path/to/video.mp4 --output audio.wav
```

#### Transcribe audio to text:
```bash
./scripts/transcribe.sh audio.wav --model base --language en --output transcript.txt
```

#### Complete pipeline (video → text):
```bash
./scripts/video_to_text.sh /path/to/video.mp4 --model small --output transcript.txt
```

#### Extract frames from video:
```bash
./scripts/extract_frames.sh /path/to/video.mp4 --interval 10 --output frames/
```

## 📋 Script Reference

### `video_info.sh`
Get detailed information about a video file.

**Options:**
- `--json` - Output in JSON format

### `extract_audio.sh`  
Extract audio from video file.

**Options:**
- `--output <file>` - Output audio file
- `--format <mp3|wav|flac>` - Output format (default: wav)
- `--quality <n>` - MP3 bitrate in kbps (default: 192)

### `transcribe.sh`
Transcribe audio file to text using Whisper.

**Options:**
- `--model <name>` - Whisper model: tiny, base, small, medium, large
- `--language <code>` - Language code (en, zh, ja, etc.)
- `--output <file>` - Output file
- `--format <txt|json|srt|vtt>` - Output format
- `--task <transcribe|translate>` - Task type

### `video_to_text.sh`
Complete pipeline: video → audio → text.

**Options:**
- All options from `transcribe.sh`
- `--keep-audio` - Keep intermediate audio file
- `--audio-format <wav|mp3>` - Intermediate audio format

### `extract_frames.sh`
Extract frames from video at intervals.

**Options:**
- `--output <dir>` - Output directory
- `--interval <n>` - Extract frame every N seconds
- `--count <n>` - Extract exactly N frames
- `--format <jpg|png>` - Image format
- `--size <WxH>` - Resize frames
- `--time <HH:MM:SS>` - Extract at specific time

## 🎛️ Whisper Model Selection

Choose model based on your needs:

| Model | Size | Speed | Accuracy | Use Case |
|-------|------|-------|----------|----------|
| `tiny` | ~75MB | ⚡ Fastest | ⭐ Low | Quick previews, short clips |
| `base` | ~140MB | 🚀 Fast | ⭐⭐ Good | General purpose (default) |
| `small` | ~460MB | 🐢 Medium | ⭐⭐⭐ Better | Important content |
| `medium` | ~1.5GB | 🐌 Slow | ⭐⭐⭐⭐ High | Professional transcription |
| `large` | ~3GB | 🐌🐌 Slowest | ⭐⭐⭐⭐⭐ Best | Research, critical content |

**Tip:** Start with `base` model, upgrade to `small` or `medium` if accuracy is important.

## 🌐 Language Support

Whisper supports 99+ languages including:
- English (`en`)
- Chinese (`zh`)
- Japanese (`ja`)
- Korean (`ko`)
- Spanish (`es`)
- French (`fr`)
- German (`de`)
- Russian (`ru`)
- Arabic (`ar`)
- And many more...

Auto-detection works well, but specifying language can improve accuracy.

## 💾 Output Formats

### Text (`txt`)
Plain text transcription.

### JSON (`json`)
Structured output with timestamps, confidence scores, and segments.

### SRT (`srt`)
SubRip subtitles format for video players.

### VTT (`vtt`)
WebVTT format for web video players.

## ⚡ Performance Tips

1. **For short videos**: Use `tiny` or `base` model
2. **For high accuracy**: Use `small` or `medium` model  
3. **For multiple files**: Process in parallel if possible
4. **For large videos**: Extract audio first, then transcribe
5. **GPU acceleration**: Install CUDA for faster transcription

## 🛠️ System Requirements

### Minimum
- Linux, macOS, or Windows (WSL)
- Python 3.7+
- FFmpeg
- 2GB free disk space
- 4GB RAM

### Recommended  
- 8GB+ RAM
- 10GB+ free disk space (for large models)
- GPU with CUDA support (for faster transcription)

## 🔧 Installation Details

The installation script will:
1. Install FFmpeg (video/audio processing)
2. Install Python 3 and pip (if not present)
3. Install OpenAI Whisper (speech-to-text)
4. Install pydub (audio processing)
5. Make all scripts executable

## 🐛 Troubleshooting

### Common Issues

**FFmpeg not found:**
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg
```

**Whisper installation fails:**
```bash
# Try with pip
pip3 install openai-whisper

# Or from GitHub
pip3 install git+https://github.com/openai/whisper.git
```

**Out of memory:**
- Use smaller Whisper model (`tiny` or `base`)
- Split large audio files
- Close other applications

**Slow transcription:**
- Use smaller model
- Enable GPU if available
- Reduce audio quality before transcription

### Debug Mode
Add `--verbose` flag to any script for detailed output.

## 📚 Examples

### Example 1: Transcribe meeting recording
```bash
./scripts/video_to_text.sh meeting.mp4 \
  --model small \
  --language en \
  --output meeting_transcript.txt \
  --format txt
```

### Example 2: Create subtitles for video
```bash
./scripts/video_to_text.sh tutorial.mp4 \
  --model base \
  --language zh \
  --output subtitles.srt \
  --format srt
```

### Example 3: Extract key frames for analysis
```bash
./scripts/extract_frames.sh presentation.mp4 \
  --interval 30 \
  --output key_frames/ \
  --format png \
  --size 1280x720
```

### Example 4: Batch process multiple videos
```bash
for video in *.mp4; do
  ./scripts/video_to_text.sh "$video" \
    --model base \
    --output "${video%.mp4}_transcript.txt"
done
```

## 🔒 Security & Privacy

- **All processing is local** - No data sent to external servers
- **Open source tools** - FFmpeg and Whisper are open source
- **No API keys required** - Works completely offline after model download
- **Data stays on your machine** - Full control over your media files

## 📄 License

This skill is MIT licensed. It uses:
- FFmpeg (LGPL/GPL)
- OpenAI Whisper (MIT)
- pydub (MIT)

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Search existing issues
3. Create a new issue with details

## 🚀 Advanced Usage

### GPU Acceleration
If you have an NVIDIA GPU with CUDA:
```bash
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Custom Models
You can use custom Whisper models:
```bash
# Download and use custom model
./scripts/transcribe.sh audio.wav --model /path/to/custom/model
```

### Integration with OpenClaw
Use this skill in your OpenClaw workflows:
```bash
# In your OpenClaw scripts
VIDEO_FILE="/path/to/video.mp4"
TRANSCRIPT=$(./scripts/video_to_text.sh "$VIDEO_FILE" --model base --format txt)
echo "Transcript: $TRANSCRIPT"
```

---

**Happy video processing and transcription! 🎬➡️📝**