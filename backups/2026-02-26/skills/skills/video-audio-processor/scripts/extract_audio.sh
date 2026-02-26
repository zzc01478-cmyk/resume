#!/usr/bin/env bash
set -euo pipefail

# Extract audio from video file

usage() {
  cat >&2 <<'EOF'
Audio Extractor from Video
Usage: extract_audio.sh <video-file> [--output <audio-file>] [--format <mp3|wav|flac>]

Extracts audio from a video file and saves it as an audio file.

Options:
  --output <file>    Output audio file (default: <video-name>.wav)
  --format <format>  Output format: mp3, wav, flac (default: wav)
  --quality <n>      For MP3: bitrate in kbps (default: 192)
  --help             Show this help message

Examples:
  extract_audio.sh video.mp4
  extract_audio.sh video.mp4 --output audio.mp3 --format mp3
  extract_audio.sh video.mp4 --format wav --output high_quality.wav
EOF
  exit 2
}

if [[ "${1:-}" == "" || "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
fi

VIDEO_FILE="$1"
shift

OUTPUT_FILE=""
FORMAT="wav"
QUALITY=192

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --output)
      OUTPUT_FILE="$2"
      shift 2
      ;;
    --format)
      FORMAT="$2"
      shift 2
      ;;
    --quality)
      QUALITY="$2"
      shift 2
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

# Check for ffmpeg
if ! command -v ffmpeg &> /dev/null; then
  echo "Error: ffmpeg is required but not installed" >&2
  echo "Install with: apt-get install ffmpeg" >&2
  exit 1
fi

# Set default output filename if not provided
if [[ -z "$OUTPUT_FILE" ]]; then
  BASENAME=$(basename "$VIDEO_FILE" | sed 's/\.[^.]*$//')
  OUTPUT_FILE="${BASENAME}.${FORMAT}"
fi

# Ensure output directory exists
mkdir -p "$(dirname "$OUTPUT_FILE")"

echo "Extracting audio from: $VIDEO_FILE"
echo "Output: $OUTPUT_FILE"
echo "Format: $FORMAT"

# Extract audio based on format
case "$FORMAT" in
  mp3)
    echo "Quality: ${QUALITY}kbps"
    ffmpeg -i "$VIDEO_FILE" -q:a 0 -map a -b:a "${QUALITY}k" -y "$OUTPUT_FILE" 2>/dev/null
    ;;
  wav)
    ffmpeg -i "$VIDEO_FILE" -vn -acodec pcm_s16le -ar 44100 -ac 2 -y "$OUTPUT_FILE" 2>/dev/null
    ;;
  flac)
    ffmpeg -i "$VIDEO_FILE" -vn -acodec flac -compression_level 5 -y "$OUTPUT_FILE" 2>/dev/null
    ;;
  *)
    echo "Error: Unsupported format: $FORMAT" >&2
    echo "Supported formats: mp3, wav, flac" >&2
    exit 1
    ;;
esac

# Check if extraction was successful
if [[ $? -eq 0 ]] && [[ -f "$OUTPUT_FILE" ]]; then
  echo "✅ Audio extraction successful!"
  echo "Output file: $OUTPUT_FILE"
  echo "File size: $(du -h "$OUTPUT_FILE" | cut -f1)"
  
  # Show audio info
  echo ""
  echo "=== Audio Information ==="
  ffprobe -v error -select_streams a:0 -show_entries stream=codec_name,sample_rate,channels,duration,bit_rate -of default=noprint_wrappers=1 "$OUTPUT_FILE" 2>/dev/null || echo "Could not get audio info"
else
  echo "❌ Audio extraction failed" >&2
  exit 1
fi