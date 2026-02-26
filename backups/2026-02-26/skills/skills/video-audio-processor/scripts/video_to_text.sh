#!/usr/bin/env bash
set -euo pipefail

# Complete pipeline: Video → Audio → Text

usage() {
  cat >&2 <<'EOF'
Video to Text Pipeline
Usage: video_to_text.sh <video-file> [options]

Complete pipeline: Extract audio from video and transcribe to text.

Options:
  --model <name>      Whisper model: tiny, base, small, medium, large (default: base)
  --language <code>   Language code: en, zh, ja, etc. (default: auto-detect)
  --output <file>     Output text file (default: <video-name>.txt)
  --format <format>   Output format: txt, json, srt, vtt (default: txt)
  --keep-audio        Keep intermediate audio file
  --audio-format <f>  Intermediate audio format: wav, mp3 (default: wav)
  --verbose           Show detailed output
  --help              Show this help message

Examples:
  video_to_text.sh video.mp4
  video_to_text.sh video.mp4 --model small --language zh --output transcript.txt
  video_to_text.sh video.mp4 --format srt --output subtitles.srt
  video_to_text.sh video.mp4 --keep-audio --verbose
EOF
  exit 2
}

if [[ "${1:-}" == "" || "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
fi

VIDEO_FILE="$1"
shift

MODEL="base"
LANGUAGE=""
OUTPUT_FILE=""
FORMAT="txt"
KEEP_AUDIO=false
AUDIO_FORMAT="wav"
VERBOSE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --model)
      MODEL="$2"
      shift 2
      ;;
    --language)
      LANGUAGE="$2"
      shift 2
      ;;
    --output)
      OUTPUT_FILE="$2"
      shift 2
      ;;
    --format)
      FORMAT="$2"
      shift 2
      ;;
    --keep-audio)
      KEEP_AUDIO=true
      shift
      ;;
    --audio-format)
      AUDIO_FORMAT="$2"
      shift 2
      ;;
    --verbose)
      VERBOSE=true
      shift
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      ;;
  esac
done

# Check if file exists
if [[ ! -f "$VIDEO_FILE" ]]; then
  echo "Error: File not found: $VIDEO_FILE" >&2
  exit 1
fi

# Check for required tools
if ! command -v ffmpeg &> /dev/null; then
  echo "Error: ffmpeg is required but not installed" >&2
  echo "Install with: apt-get install ffmpeg" >&2
  exit 1
fi

if ! python3 -c "import whisper" 2>/dev/null; then
  echo "Error: OpenAI Whisper is not installed" >&2
  echo "Install with: pip install openai-whisper" >&2
  exit 1
fi

# Set default output filename if not provided
if [[ -z "$OUTPUT_FILE" ]]; then
  BASENAME=$(basename "$VIDEO_FILE" | sed 's/\.[^.]*$//')
  OUTPUT_FILE="${BASENAME}.${FORMAT}"
fi

# Create temporary directory for intermediate files
TEMP_DIR=$(mktemp -d)
trap '[[ $KEEP_AUDIO == "false" ]] && rm -rf "$TEMP_DIR"' EXIT

echo "🚀 Starting Video to Text Pipeline"
echo "Input video: $VIDEO_FILE"
echo "Output: $OUTPUT_FILE"
echo ""

# Step 1: Get video information
echo "=== Step 1: Analyzing Video ==="
VIDEO_DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$VIDEO_FILE" 2>/dev/null || echo "unknown")
echo "Duration: ${VIDEO_DURATION}s"
echo ""

# Step 2: Extract audio
echo "=== Step 2: Extracting Audio ==="
AUDIO_FILE="$TEMP_DIR/audio.$AUDIO_FORMAT"

if [[ "$VERBOSE" == "true" ]]; then
  ./extract_audio.sh "$VIDEO_FILE" --output "$AUDIO_FILE" --format "$AUDIO_FORMAT"
else
  ./extract_audio.sh "$VIDEO_FILE" --output "$AUDIO_FILE" --format "$AUDIO_FORMAT" 2>/dev/null
  echo "✅ Audio extracted: $AUDIO_FILE"
fi
echo ""

# Step 3: Transcribe audio
echo "=== Step 3: Transcribing Audio ==="
TRANSCRIBE_ARGS="--model $MODEL --format $FORMAT --output $OUTPUT_FILE"
[[ -n "$LANGUAGE" ]] && TRANSCRIBE_ARGS="$TRANSCRIBE_ARGS --language $LANGUAGE"
[[ "$VERBOSE" == "true" ]] && TRANSCRIBE_ARGS="$TRANSCRIBE_ARGS --verbose"

if [[ "$VERBOSE" == "true" ]]; then
  ./transcribe.sh "$AUDIO_FILE" $TRANSCRIBE_ARGS
else
  echo "Using Whisper model: $MODEL"
  ./transcribe.sh "$AUDIO_FILE" $TRANSCRIBE_ARGS 2>/dev/null
  echo "✅ Transcription completed"
fi
echo ""

# Step 4: Cleanup and final output
echo "=== Step 4: Finalizing ==="
if [[ "$KEEP_AUDIO" == "true" ]]; then
  FINAL_AUDIO="${OUTPUT_FILE%.*}.$AUDIO_FORMAT"
  cp "$AUDIO_FILE" "$FINAL_AUDIO"
  echo "Audio file kept: $FINAL_AUDIO"
else
  echo "Intermediate audio file removed"
fi

echo ""
echo "🎉 Pipeline Completed Successfully!"
echo ""
echo "📊 Summary:"
echo "  Input video: $(basename "$VIDEO_FILE")"
echo "  Video duration: ${VIDEO_DURATION}s"
echo "  Whisper model: $MODEL"
[[ -n "$LANGUAGE" ]] && echo "  Language: $LANGUAGE"
echo "  Output format: $FORMAT"
echo "  Output file: $OUTPUT_FILE"
echo "  Output size: $(du -h "$OUTPUT_FILE" 2>/dev/null | cut -f1 || echo "unknown")"

if [[ "$FORMAT" == "txt" ]] && [[ -f "$OUTPUT_FILE" ]]; then
  echo ""
  echo "📝 Transcription Preview:"
  head -5 "$OUTPUT_FILE"
  echo "..."
  echo "Total lines: $(wc -l < "$OUTPUT_FILE")"
  echo "Total words: $(wc -w < "$OUTPUT_FILE")"
fi