#!/usr/bin/env bash
set -euo pipefail

# Video information extractor using ffmpeg and mediainfo

usage() {
  cat >&2 <<'EOF'
Video Information Extractor
Usage: video_info.sh <video-file> [--json]

Extracts detailed information about a video file including:
- Format, codec, resolution, duration
- Audio tracks information
- Metadata (if available)

Options:
  --json    Output in JSON format (default: human readable)
  --help    Show this help message

Examples:
  video_info.sh video.mp4
  video_info.sh video.mp4 --json
EOF
  exit 2
}

if [[ "${1:-}" == "" || "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
fi

VIDEO_FILE="$1"
JSON_OUTPUT=false

# Parse arguments
shift
while [[ $# -gt 0 ]]; do
  case "$1" in
    --json)
      JSON_OUTPUT=true
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

# Function to get video info using ffmpeg
get_ffmpeg_info() {
  local file="$1"
  
  # Get basic info
  ffmpeg -i "$file" 2>&1 | grep -E "Duration|Stream|bitrate" || true
  
  # Get more detailed info
  echo ""
  echo "=== Detailed Stream Information ==="
  ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,width,height,pix_fmt,r_frame_rate,duration,bit_rate -of default=noprint_wrappers=1 "$file"
  
  if ffprobe -v error -select_streams a:0 -show_entries stream=codec_name,sample_rate,channels,bit_rate -of default=noprint_wrappers=1 "$file" 2>/dev/null; then
    echo ""
    echo "=== Audio Stream Information ==="
    ffprobe -v error -select_streams a -show_entries stream=codec_name,sample_rate,channels,bit_rate -of default=noprint_wrappers=1 "$file"
  fi
}

# Function to get JSON output
get_json_info() {
  local file="$1"
  
  # Use ffprobe to get JSON output
  ffprobe -v quiet -print_format json -show_format -show_streams "$file" 2>/dev/null || echo "{}"
}

# Main execution
echo "Analyzing: $VIDEO_FILE"
echo "File size: $(du -h "$VIDEO_FILE" | cut -f1)"
echo ""

if [[ "$JSON_OUTPUT" == "true" ]]; then
  get_json_info "$VIDEO_FILE"
else
  get_ffmpeg_info "$VIDEO_FILE"
  
  # Additional info if mediainfo is available
  if command -v mediainfo &> /dev/null; then
    echo ""
    echo "=== MediaInfo Output ==="
    mediainfo "$VIDEO_FILE" | head -50
  else
    echo ""
    echo "Note: Install 'mediainfo' for more detailed information"
    echo "      apt-get install mediainfo"
  fi
fi