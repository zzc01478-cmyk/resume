#!/usr/bin/env bash
set -euo pipefail

# Install dependencies for video-audio-processor

echo "🔧 Installing dependencies for Video & Audio Processor"
echo "=".repeat(60)

# Detect OS
if [[ -f /etc/os-release ]]; then
  . /etc/os-release
  OS=$ID
else
  OS=$(uname -s)
fi

echo "Detected OS: $OS"
echo ""

# Function to check if command exists
command_exists() {
  command -v "$1" &> /dev/null
}

# Function to install with apt
install_apt() {
  echo "Installing $1..."
  apt-get update && apt-get install -y "$1"
}

# Function to install with pip
install_pip() {
  echo "Installing Python package: $1..."
  pip3 install "$1"
}

# Check and install ffmpeg
echo "=== Checking ffmpeg ==="
if command_exists ffmpeg; then
  echo "✅ ffmpeg is already installed"
  ffmpeg -version | head -1
else
  echo "❌ ffmpeg not found, installing..."
  
  case $OS in
    ubuntu|debian)
      install_apt ffmpeg
      ;;
    fedora)
      dnf install -y ffmpeg
      ;;
    centos|rhel)
      yum install -y ffmpeg
      ;;
    alpine)
      apk add ffmpeg
      ;;
    *)
      echo "⚠️  Unsupported OS for automatic ffmpeg installation"
      echo "Please install ffmpeg manually: https://ffmpeg.org/download.html"
      ;;
  esac
  
  if command_exists ffmpeg; then
    echo "✅ ffmpeg installed successfully"
  else
    echo "❌ ffmpeg installation failed"
    exit 1
  fi
fi
echo ""

# Check and install Python3/pip
echo "=== Checking Python3 ==="
if command_exists python3; then
  echo "✅ Python3 is already installed"
  python3 --version
else
  echo "❌ Python3 not found, installing..."
  
  case $OS in
    ubuntu|debian)
      install_apt python3 python3-pip
      ;;
    fedora)
      dnf install -y python3 python3-pip
      ;;
    centos|rhel)
      yum install -y python3 python3-pip
      ;;
    alpine)
      apk add python3 py3-pip
      ;;
    *)
      echo "⚠️  Unsupported OS for automatic Python installation"
      echo "Please install Python3 manually: https://www.python.org/downloads/"
      ;;
  esac
  
  if command_exists python3; then
    echo "✅ Python3 installed successfully"
  else
    echo "❌ Python3 installation failed"
    exit 1
  fi
fi
echo ""

# Check and install Whisper
echo "=== Checking OpenAI Whisper ==="
if python3 -c "import whisper" 2>/dev/null; then
  echo "✅ OpenAI Whisper is already installed"
  python3 -c "import whisper; print(f'Whisper version: {whisper.__version__}')" 2>/dev/null || echo "Version unknown"
else
  echo "❌ OpenAI Whisper not found, installing..."
  install_pip openai-whisper
  
  if python3 -c "import whisper" 2>/dev/null; then
    echo "✅ OpenAI Whisper installed successfully"
    echo "Note: First transcription will download the model (100MB-3GB)"
  else
    echo "❌ OpenAI Whisper installation failed"
    echo "Trying alternative installation method..."
    pip3 install git+https://github.com/openai/whisper.git
  fi
fi
echo ""

# Check and install pydub
echo "=== Checking pydub ==="
if python3 -c "import pydub" 2>/dev/null; then
  echo "✅ pydub is already installed"
else
  echo "❌ pydub not found, installing..."
  install_pip pydub
  
  # pydub requires ffmpeg, which we already installed
  if python3 -c "import pydub" 2>/dev/null; then
    echo "✅ pydub installed successfully"
  else
    echo "⚠️  pydub installation may have issues, but continuing..."
  fi
fi
echo ""

# Optional: Check and install ImageMagick for contact sheets
echo "=== Checking ImageMagick (optional) ==="
if command_exists montage; then
  echo "✅ ImageMagick is already installed"
else
  echo "ℹ️  ImageMagick not found (optional for contact sheets)"
  echo "To install:"
  echo "  Ubuntu/Debian: apt-get install imagemagick"
  echo "  macOS: brew install imagemagick"
fi
echo ""

# Make all scripts executable
echo "=== Setting up scripts ==="
SCRIPT_DIR=$(dirname "$0")
chmod +x "$SCRIPT_DIR"/*.sh
echo "✅ All scripts are now executable"
echo ""

# Test installation
echo "=== Testing installation ==="
echo "Testing ffmpeg..."
ffmpeg -version | head -1

echo ""
echo "Testing Python packages..."
python3 -c "
try:
    import whisper
    print('✅ Whisper: OK')
except ImportError:
    print('❌ Whisper: FAILED')

try:
    import pydub
    print('✅ pydub: OK')
except ImportError:
    print('❌ pydub: FAILED')
"

echo ""
echo "=".repeat(60)
echo "🎉 Installation completed successfully!"
echo ""
echo "📚 Usage examples:"
echo "  1. Get video info: ./video_info.sh video.mp4"
echo "  2. Extract audio: ./extract_audio.sh video.mp4 --output audio.wav"
echo "  3. Transcribe audio: ./transcribe.sh audio.wav --model base"
echo "  4. Video to text: ./video_to_text.sh video.mp4 --output transcript.txt"
echo "  5. Extract frames: ./extract_frames.sh video.mp4 --interval 10"
echo ""
echo "💡 First transcription will download the Whisper model"
echo "   Choose model size based on your needs:"
echo "   - tiny: Fastest, lowest accuracy"
echo "   - base: Good balance (default)"
echo "   - small: Better accuracy"
echo "   - medium: High accuracy"
echo "   - large: Best accuracy, slowest"
echo ""
echo "⚠️  Note: Large models require significant disk space (up to 3GB)"