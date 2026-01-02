#!/bin/bash
set -euo pipefail

echo "=================================================="
echo "  TikTok Video Automation - Setup Script"
echo "  @kavalier_cc"
echo "=================================================="

# Update system
echo -e "\n[1/4] Updating system packages..."
sudo apt-get update

# Install system dependencies
echo -e "\n[2/4] Installing ffmpeg and ImageMagick..."
sudo apt-get install -y \
    ffmpeg \
    libavcodec-dev \
    libavformat-dev \
    libavutil-dev \
    libavdevice-dev \
    libavfilter-dev \
    libswscale-dev \
    libswresample-dev \
    imagemagick \
    nodejs npm \
    fonts-dejavu-core \
    fonts-freefont-ttf

# Confirm AAC encoder availability (needed for final audio mux)
ffmpeg -hide_banner -codecs | grep -m1 "EA.. aac" || echo "Warning: AAC encoder not found"

# Relax ImageMagick policy for moviepy TextClip
echo -e "\n[2b/4] Adjusting ImageMagick policy..."
sudo sed -i 's/<policy domain="path" rights="none" pattern="@\*"\/>/<!-- moviepy enable @files --><policy domain="path" rights="read|write" pattern="@*"\/>/' /etc/ImageMagick-6/policy.xml 2>/dev/null || true
sudo sed -i 's/<policy domain="path" rights="none" pattern="@\*"\/>/<!-- moviepy enable @files --><policy domain="path" rights="read|write" pattern="@*"\/>/' /etc/ImageMagick-7/policy.xml 2>/dev/null || true

# Install Python dependencies
echo -e "\n[3/4] Installing Python packages..."
pip install --upgrade pip

# Install moviepy dependencies first to avoid av compilation issues
echo "Installing moviepy dependencies..."
pip install Decorator imageio==2.31.1 imageio-ffmpeg numpy==1.26.4 proglog tqdm

# Install moviepy without building av from source
echo "Installing moviepy..."
pip install moviepy==1.0.3 --no-deps

# Install remaining packages (openai-whisper instead of faster-whisper)
echo "Installing remaining packages..."
pip install pytubefix openai-whisper opencv-python torch youtube-search-python httpx==0.24.1 yt-dlp

# Create necessary directories
echo -e "\n[4/4] Creating directories..."
mkdir -p video_audio

echo -e "\n✅ Setup complete!"
echo -e "\n📝 Next steps:"
echo "  1. Make sure your API keys are in settings.json"
echo "  2. Run: python short_create.py"
echo -e "\n=================================================="
