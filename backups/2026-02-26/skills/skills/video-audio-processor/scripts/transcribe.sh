#!/usr/bin/env bash
set -euo pipefail

# Audio transcription using OpenAI Whisper

usage() {
  cat >&2 <<'EOF'
Audio Transcription with Whisper
Usage: transcribe.sh <audio-file> [options]

Transcribes audio file to text using OpenAI Whisper.

Required: Install Whisper first: pip install openai-whisper

Options:
  --model <name>      Whisper model: tiny, base, small, medium, large (default: base)
  --language <code>   Language code: en, zh, ja, etc. (default: auto-detect)
  --output <file>     Output file (default: <audio-name>.txt)
  --format <format>   Output format: txt, json, srt, vtt (default: txt)
  --task <task>       Task: transcribe or translate (default: transcribe)
  --verbose           Show detailed output
  --help              Show this help message

Examples:
  transcribe.sh audio.wav
  transcribe.sh audio.wav --model small --language en --output transcript.txt
  transcribe.sh audio.wav --format json --output transcript.json
  transcribe.sh audio.wav --task translate --language en  # Translate to English
EOF
  exit 2
}

if [[ "${1:-}" == "" || "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
fi

AUDIO_FILE="$1"
shift

MODEL="base"
LANGUAGE=""
OUTPUT_FILE=""
FORMAT="txt"
TASK="transcribe"
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
    --task)
      TASK="$2"
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
if [[ ! -f "$AUDIO_FILE" ]]; then
  echo "Error: File not found: $AUDIO_FILE" >&2
  exit 1
fi

# Check for Whisper
if ! python3 -c "import whisper" 2>/dev/null; then
  echo "Error: OpenAI Whisper is not installed" >&2
  echo "Install with: pip install openai-whisper" >&2
  echo "Note: First run will download the model (100MB-3GB)" >&2
  exit 1
fi

# Set default output filename if not provided
if [[ -z "$OUTPUT_FILE" ]]; then
  BASENAME=$(basename "$AUDIO_FILE" | sed 's/\.[^.]*$//')
  OUTPUT_FILE="${BASENAME}.${FORMAT}"
fi

# Ensure output directory exists
mkdir -p "$(dirname "$OUTPUT_FILE")"

echo "Transcribing: $AUDIO_FILE"
echo "Model: $MODEL"
echo "Task: $TASK"
echo "Output: $OUTPUT_FILE"
echo "Format: $FORMAT"
[[ -n "$LANGUAGE" ]] && echo "Language: $LANGUAGE"
echo ""

# Build Whisper command
WHISPER_CMD="python3 -c \"
import whisper
import json
import sys

# Load model
model = whisper.load_model('$MODEL')

# Transcribe audio
result = model.transcribe(
    '$AUDIO_FILE',
    language='$LANGUAGE' if '$LANGUAGE' else None,
    task='$TASK',
    verbose=$VERBOSE
)

# Save output based on format
if '$FORMAT' == 'txt':
    with open('$OUTPUT_FILE', 'w', encoding='utf-8') as f:
        f.write(result['text'])
    print(f'Transcription saved to: $OUTPUT_FILE')
    
elif '$FORMAT' == 'json':
    with open('$OUTPUT_FILE', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f'JSON transcription saved to: $OUTPUT_FILE')
    
elif '$FORMAT' == 'srt':
    from whisper.utils import write_srt
    with open('$OUTPUT_FILE', 'w', encoding='utf-8') as f:
        write_srt(result['segments'], file=f)
    print(f'SRT subtitles saved to: $OUTPUT_FILE')
    
elif '$FORMAT' == 'vtt':
    from whisper.utils import write_vtt
    with open('$OUTPUT_FILE', 'w', encoding='utf-8') as f:
        write_vtt(result['segments'], file=f)
    print(f'VTT subtitles saved to: $OUTPUT_FILE')
    
else:
    print(f'Error: Unknown format: $FORMAT')
    sys.exit(1)
\""

# Execute Whisper command
eval "$WHISPER_CMD"

if [[ $? -eq 0 ]] && [[ -f "$OUTPUT_FILE" ]]; then
  echo "✅ Transcription successful!"
  echo ""
  
  # Show summary
  if [[ "$FORMAT" == "txt" ]]; then
    echo "=== Transcription Preview ==="
    head -10 "$OUTPUT_FILE"
    echo ""
    echo "Total lines: $(wc -l < "$OUTPUT_FILE")"
    echo "Total words: $(wc -w < "$OUTPUT_FILE")"
  elif [[ "$FORMAT" == "json" ]]; then
    echo "JSON output with segments and timestamps"
  elif [[ "$FORMAT" == "srt" ]] || [[ "$FORMAT" == "vtt" ]]; then
    echo "Subtitles with timestamps"
  fi
  
  echo ""
  echo "File size: $(du -h "$OUTPUT_FILE" | cut -f1)"
else
  echo "❌ Transcription failed" >&2
  exit 1
fi