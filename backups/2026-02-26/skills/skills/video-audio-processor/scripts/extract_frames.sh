#!/usr/bin/env bash
set -euo pipefail

# Extract frames from video at intervals

usage() {
  cat >&2 <<'EOF'
Video Frame Extractor
Usage: extract_frames.sh <video-file> [options]

Extracts frames from video at specified intervals.

Options:
  --output <dir>      Output directory (default: frames_<video-name>)
  --interval <n>      Extract frame every N seconds (default: 10)
  --count <n>         Extract exactly N frames evenly spaced
  --format <format>   Image format: jpg, png (default: jpg)
  --quality <n>       JPEG quality 1-100 (default: 90)
  --size <WxH>        Resize frames (e.g., 640x480)
  --time <HH:MM:SS>   Extract frame at specific time
  --times <t1,t2,...> Extract frames at multiple times
  --verbose           Show detailed output
  --help              Show this help message

Examples:
  extract_frames.sh video.mp4
  extract_frames.sh video.mp4 --interval 5 --output my_frames
  extract_frames.sh video.mp4 --count 20 --format png
  extract_frames.sh video.mp4 --time 00:01:30 --output keyframe.jpg
  extract_frames.sh video.mp4 --times "00:00:10,00:01:00,00:02:30"
EOF
  exit 2
}

if [[ "${1:-}" == "" || "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
fi

VIDEO_FILE="$1"
shift

OUTPUT_DIR=""
INTERVAL=10
COUNT=0
FORMAT="jpg"
QUALITY=90
SIZE=""
SPECIFIC_TIME=""
TIMES=""
VERBOSE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --output)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    --interval)
      INTERVAL="$2"
      shift 2
      ;;
    --count)
      COUNT="$2"
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
    --size)
      SIZE="$2"
      shift 2
      ;;
    --time)
      SPECIFIC_TIME="$2"
      shift 2
      ;;
    --times)
      TIMES="$2"
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

# Check for ffmpeg
if ! command -v ffmpeg &> /dev/null; then
  echo "Error: ffmpeg is required but not installed" >&2
  echo "Install with: apt-get install ffmpeg" >&2
  exit 1
fi

# Get video duration
DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$VIDEO_FILE" 2>/dev/null || echo "0")
DURATION=${DURATION%.*}

if [[ "$DURATION" == "0" ]]; then
  echo "Warning: Could not get video duration" >&2
fi

# Set default output directory
if [[ -z "$OUTPUT_DIR" ]]; then
  BASENAME=$(basename "$VIDEO_FILE" | sed 's/\.[^.]*$//')
  OUTPUT_DIR="frames_${BASENAME}"
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "Extracting frames from: $VIDEO_FILE"
echo "Output directory: $OUTPUT_DIR"
[[ "$DURATION" != "0" ]] && echo "Video duration: ${DURATION}s"
echo ""

# Build ffmpeg filter based on options
FFMPEG_FILTER=""
FFMPEG_ARGS=""

# Add resize if specified
if [[ -n "$SIZE" ]]; then
  FFMPEG_FILTER="scale=$SIZE"
fi

# Add format-specific quality
if [[ "$FORMAT" == "jpg" ]] || [[ "$FORMAT" == "jpeg" ]]; then
  FFMPEG_ARGS="-q:v $QUALITY"
fi

# Case 1: Extract frame at specific time
if [[ -n "$SPECIFIC_TIME" ]]; then
  OUTPUT_FILE="$OUTPUT_DIR/frame_$(echo "$SPECIFIC_TIME" | tr ':' '_').$FORMAT"
  
  echo "Extracting frame at: $SPECIFIC_TIME"
  echo "Output: $OUTPUT_FILE"
  
  if [[ "$VERBOSE" == "true" ]]; then
    ffmpeg -ss "$SPECIFIC_TIME" -i "$VIDEO_FILE" -frames:v 1 $FFMPEG_ARGS -y "$OUTPUT_FILE"
  else
    ffmpeg -hide_banner -loglevel error -ss "$SPECIFIC_TIME" -i "$VIDEO_FILE" -frames:v 1 $FFMPEG_ARGS -y "$OUTPUT_FILE"
  fi
  
  if [[ -f "$OUTPUT_FILE" ]]; then
    echo "✅ Frame extracted successfully"
    echo "File size: $(du -h "$OUTPUT_FILE" | cut -f1)"
  else
    echo "❌ Frame extraction failed" >&2
    exit 1
  fi
  
  exit 0
fi

# Case 2: Extract frames at specific times
if [[ -n "$TIMES" ]]; then
  IFS=',' read -ra TIME_ARRAY <<< "$TIMES"
  echo "Extracting ${#TIME_ARRAY[@]} frames at specified times"
  
  for i in "${!TIME_ARRAY[@]}"; do
    TIME="${TIME_ARRAY[$i]}"
    OUTPUT_FILE="$OUTPUT_DIR/frame_$(printf "%03d" $i)_$(echo "$TIME" | tr ':' '_').$FORMAT"
    
    echo "  $TIME → $OUTPUT_FILE"
    
    if [[ "$VERBOSE" == "true" ]]; then
      ffmpeg -ss "$TIME" -i "$VIDEO_FILE" -frames:v 1 $FFMPEG_ARGS -y "$OUTPUT_FILE" 2>&1 | tail -5
    else
      ffmpeg -hide_banner -loglevel error -ss "$TIME" -i "$VIDEO_FILE" -frames:v 1 $FFMPEG_ARGS -y "$OUTPUT_FILE"
    fi
  done
  
  FRAME_COUNT=$(ls -1 "$OUTPUT_DIR"/*."$FORMAT" 2>/dev/null | wc -l)
  echo ""
  echo "✅ Extracted $FRAME_COUNT frames"
  exit 0
fi

# Case 3: Extract N frames evenly spaced
if [[ "$COUNT" -gt 0 ]]; then
  echo "Extracting $COUNT frames evenly spaced"
  
  # Calculate interval between frames
  if [[ "$DURATION" != "0" ]] && [[ "$DURATION" -gt 0 ]]; then
    INTERVAL_SECONDS=$((DURATION / COUNT))
  else
    INTERVAL_SECONDS=10
    echo "Warning: Using default interval of ${INTERVAL_SECONDS}s"
  fi
  
  FFMPEG_FILTER="fps=1/$INTERVAL_SECONDS${FFMPEG_FILTER:+,$FFMPEG_FILTER}"
  OUTPUT_PATTERN="$OUTPUT_DIR/frame_%03d.$FORMAT"
  
  if [[ "$VERBOSE" == "true" ]]; then
    ffmpeg -i "$VIDEO_FILE" -vf "$FFMPEG_FILTER" $FFMPEG_ARGS -y "$OUTPUT_PATTERN"
  else
    ffmpeg -hide_banner -loglevel error -i "$VIDEO_FILE" -vf "$FFMPEG_FILTER" $FFMPEG_ARGS -y "$OUTPUT_PATTERN"
  fi
  
# Case 4: Extract frames at regular interval
else
  echo "Extracting frames every ${INTERVAL} seconds"
  
  FFMPEG_FILTER="fps=1/$INTERVAL${FFMPEG_FILTER:+,$FFMPEG_FILTER}"
  OUTPUT_PATTERN="$OUTPUT_DIR/frame_%03d.$FORMAT"
  
  if [[ "$VERBOSE" == "true" ]]; then
    ffmpeg -i "$VIDEO_FILE" -vf "$FFMPEG_FILTER" $FFMPEG_ARGS -y "$OUTPUT_PATTERN"
  else
    ffmpeg -hide_banner -loglevel error -i "$VIDEO_FILE" -vf "$FFMPEG_FILTER" $FFMPEG_ARGS -y "$OUTPUT_PATTERN"
  fi
fi

# Count extracted frames
FRAME_COUNT=$(ls -1 "$OUTPUT_DIR"/*."$FORMAT" 2>/dev/null | wc -l)

if [[ "$FRAME_COUNT" -gt 0 ]]; then
  echo ""
  echo "✅ Successfully extracted $FRAME_COUNT frames"
  echo ""
  echo "📁 Output files in: $OUTPUT_DIR"
  echo "First few files:"
  ls -1 "$OUTPUT_DIR"/*."$FORMAT" | head -5
  
  # Create a contact sheet if ImageMagick is available
  if command -v montage &> /dev/null && [[ "$FRAME_COUNT" -ge 4 ]]; then
    CONTACT_SHEET="$OUTPUT_DIR/contact_sheet.jpg"
    echo ""
    echo "Creating contact sheet..."
    montage "$OUTPUT_DIR"/*."$FORMAT" -tile 4x -geometry +5+5 "$CONTACT_SHEET" 2>/dev/null
    if [[ -f "$CONTACT_SHEET" ]]; then
      echo "Contact sheet: $CONTACT_SHEET"
    fi
  fi
else
  echo "❌ No frames were extracted" >&2
  exit 1
fi