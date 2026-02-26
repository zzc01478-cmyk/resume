#!/usr/bin/env bash
set -euo pipefail

# Test script for video-audio-processor installation

echo "🧪 Testing Video & Audio Processor Installation"
echo "=".repeat(60)

# Test 1: Check required commands
echo "=== Test 1: Checking Required Commands ==="
ERRORS=0

check_command() {
  if command -v "$1" &> /dev/null; then
    echo "✅ $1: Found"
    return 0
  else
    echo "❌ $1: NOT FOUND"
    return 1
  fi
}

check_command ffmpeg || ERRORS=$((ERRORS + 1))
check_command python3 || ERRORS=$((ERRORS + 1))
echo ""

# Test 2: Check Python packages
echo "=== Test 2: Checking Python Packages ==="
check_python_package() {
  if python3 -c "import $1" 2>/dev/null; then
    echo "✅ $1: Installed"
    return 0
  else
    echo "❌ $1: NOT INSTALLED"
    return 1
  fi
}

check_python_package whisper || ERRORS=$((ERRORS + 1))
check_python_package pydub || ERRORS=$((ERRORS + 1))
echo ""

# Test 3: Check script permissions
echo "=== Test 3: Checking Script Permissions ==="
SCRIPT_DIR=$(dirname "$0")
for script in "$SCRIPT_DIR"/*.sh; do
  if [[ -x "$script" ]]; then
    echo "✅ $(basename "$script"): Executable"
  else
    echo "❌ $(basename "$script"): NOT executable"
    ERRORS=$((ERRORS + 1))
  fi
done
echo ""

# Test 4: Create a test video (if ffmpeg is available)
echo "=== Test 4: Testing Video Creation ==="
if [[ $ERRORS -eq 0 ]] && command -v ffmpeg &> /dev/null; then
  TEST_VIDEO="$SCRIPT_DIR/test_video.mp4"
  TEST_AUDIO="$SCRIPT_DIR/test_audio.wav"
  
  echo "Creating test video..."
  # Create a 5-second test video with color bars and beep
  ffmpeg -hide_banner -loglevel error \
    -f lavfi -i "smptebars=duration=5:size=640x480:rate=30" \
    -f lavfi -i "sine=frequency=1000:duration=5" \
    -c:v libx264 -preset ultrafast -crf 23 \
    -c:a aac -b:a 128k \
    -y "$TEST_VIDEO" 2>/dev/null
  
  if [[ -f "$TEST_VIDEO" ]]; then
    echo "✅ Test video created: $TEST_VIDEO"
    echo "   Size: $(du -h "$TEST_VIDEO" | cut -f1)"
    
    # Test video info
    echo ""
    echo "Testing video info..."
    "$SCRIPT_DIR/video_info.sh" "$TEST_VIDEO" 2>/dev/null | grep -E "Duration|Stream" | head -3
    
    # Test audio extraction
    echo ""
    echo "Testing audio extraction..."
    "$SCRIPT_DIR/extract_audio.sh" "$TEST_VIDEO" --output "$TEST_AUDIO" 2>/dev/null
    if [[ -f "$TEST_AUDIO" ]]; then
      echo "✅ Audio extracted: $TEST_AUDIO"
      
      # Cleanup test files
      rm -f "$TEST_VIDEO" "$TEST_AUDIO"
      echo "✅ Test files cleaned up"
    else
      echo "❌ Audio extraction failed"
      ERRORS=$((ERRORS + 1))
    fi
  else
    echo "❌ Test video creation failed"
    ERRORS=$((ERRORS + 1))
  fi
else
  echo "⚠️  Skipping video tests due to previous errors"
fi
echo ""

# Final summary
echo "=".repeat(60)
if [[ $ERRORS -eq 0 ]]; then
  echo "🎉 All tests passed! Installation is complete and working."
  echo ""
  echo "🚀 Ready to use:"
  echo "  1. Get video information: ./video_info.sh <video-file>"
  echo "  2. Extract audio: ./extract_audio.sh <video-file>"
  echo "  3. Transcribe audio: ./transcribe.sh <audio-file>"
  echo "  4. Complete pipeline: ./video_to_text.sh <video-file>"
  echo "  5. Extract frames: ./extract_frames.sh <video-file>"
else
  echo "⚠️  Found $ERRORS error(s)"
  echo ""
  echo "🔧 To fix installation issues:"
  echo "  1. Run the install script: ./install_deps.sh"
  echo "  2. Check your internet connection"
  echo "  3. Make sure you have sudo privileges if needed"
  echo "  4. Check system requirements:"
  echo "     - Linux/macOS/Windows (WSL)"
  echo "     - Python 3.7+"
  echo "     - FFmpeg"
  echo "     - 2GB+ free disk space for models"
  exit 1
fi