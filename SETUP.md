# 🎬 TikTok Video Automation - Setup Guide

Automatische TikTok-Style Reddit-Geschichten-Videos mit KI generieren.

---

## 🚀 Schnell-Setup (empfohlen)

### Option 1: Automatisches Setup-Skript

```bash
chmod +x build.sh
./build.sh
```

Das Skript installiert automatisch:
- ✅ ffmpeg und alle benötigten Codecs
- ✅ ImageMagick für Text-Overlays
- ✅ Alle Python-Dependencies
- ✅ Erstellt notwendige Verzeichnisse

---

### Option 2: Manuelles Setup

#### 1. System-Dependencies installieren

```bash
sudo apt-get update
sudo apt-get install -y ffmpeg libavcodec-dev libavformat-dev libavutil-dev \
    libavdevice-dev libavfilter-dev libswscale-dev libswresample-dev imagemagick nodejs npm

# ImageMagick Policy (für TextClip nötig)
sudo sed -i 's/<policy domain="path" rights="none" pattern="@\*"\/>/<!-- moviepy enable @files --><policy domain="path" rights="read|write" pattern="@*"\/>/' /etc/ImageMagick-6/policy.xml 2>/dev/null || true
sudo sed -i 's/<policy domain="path" rights="none" pattern="@\*"\/>/<!-- moviepy enable @files --><policy domain="path" rights="read|write" pattern="@*"\/>/' /etc/ImageMagick-7/policy.xml 2>/dev/null || true
```

#### 2. Python-Pakete installieren

```bash
pip install --upgrade pip

# Installiere moviepy dependencies zuerst
pip install Decorator imageio==2.31.1 imageio-ffmpeg numpy==1.26.4 proglog tqdm

# Installiere moviepy ohne av-Kompilierung
pip install moviepy==1.0.3 --no-deps

# Installiere restliche Pakete (openai-whisper statt faster-whisper wegen Python 3.12)
pip install pytubefix openai-whisper opencv-python torch youtube-search-python httpx==0.24.1 yt-dlp

### Optional: eigenes Hintergrundvideo
Lege eine Datei `video_audio/background.mp4` ab; sie wird verwendet falls YouTube-Download blockiert wird.
```

#### 3. Verzeichnisse erstellen

```bash
mkdir -p video_audio
```

---

## 🔑 API Keys konfigurieren

Bearbeite `settings.json` und füge deine API-Keys ein:

```json
{
    "path": "/workspaces/tiktok-video-automation/video_audio/",
    "groc_api_key": "DEIN_GROQ_API_KEY",
    "voicerss_api": "DEIN_VOICERSS_API_KEY",
    "watermark_text": "@kavalier_cc",
    "watermark_position": "bottom_right"
}
```

### API-Keys beziehen:

- **Groq API**: https://console.groq.com/keys (kostenlos)
- **VoiceRSS API**: https://www.voicerss.org/ (kostenlos, bis 350 Requests/Tag)

---

## 🎥 Video generieren

```bash
python short_create.py
```

### Interaktive Optionen:

**1. Modus auswählen:**
```
1) 2-PART VIDEO (Story continues in Part 2, each ~1 minute)
2) 1-PART VIDEO (Complete story in one video, ~1 minute)
```

**2. Hook-Line eingeben:**
```
Beispiel: "I got abandoned in a forest by my family, but i got revenge on them"
```

### Output:

- **2-Part Modus**: `video_audio/final_tiktok_video_PART1.mp4` + `_PART2.mp4`
- **1-Part Modus**: `video_audio/final_tiktok_video.mp4`

---

## ⚙️ Konfiguration anpassen

### Watermark ändern

In `settings.json`:

```json
"watermark_text": "@dein_username",
"watermark_position": "bottom_right"  // top_left, top_right, bottom_left, bottom_right
```

### Video-Hintergrund ändern

In `short_create.py`, Zeile ~44:

```python
yut.Download(search='minecraft parkour gameplay no copyright 4k')
```

Ändere zu z.B.:
```python
yut.Download(search='subway surfers gameplay 4k')
```

### TTS-Stimme anpassen

In `short_create.py`, Zeile ~82:

```python
voicer = random.choice(['Mike','John','Amy','Linda'])
```

Weitere Stimmen: https://www.voicerss.org/api/documentation.aspx

---

## 📋 Systemanforderungen

- **OS**: Linux (GitHub Codespaces, Ubuntu, Debian)
- **Python**: 3.8+
- **Speicher**: ~2 GB für Dependencies
- **CPU**: Mindestens 2 Cores (Whisper läuft auf CPU)

---

## 🛠️ Troubleshooting

### Problem: `ModuleNotFoundError: No module named 'moviepy'`

```bash
pip uninstall moviepy av -y
pip install Decorator imageio==2.31.1 imageio-ffmpeg numpy proglog tqdm
pip install moviepy==1.0.3 --no-deps
pip install av --only-binary=:all: || echo "av skipped - moviepy will use imageio-ffmpeg"
```

### Problem: `ERROR: Failed to build 'av'`

Das ist ein bekanntes Problem mit Python 3.12 und av 10.x. Lösung:

```bash
# Nutze vorkompilierte Binaries oder skippe av
pip install av --only-binary=:all: || echo "Skipping av"
```

Moviepy funktioniert auch ohne `av` durch `imageio-ffmpeg`.

### Problem: `Package 'libavcodec' not found`

```bash
sudo apt-get install -y ffmpeg libavcodec-dev libavformat-dev
```

### Problem: ImageMagick Fehler

```bash
sudo apt-get install -y imagemagick
```

### Problem: CUDA/GPU Fehler

Das Skript ist bereits für CPU konfiguriert (Codespaces-kompatibel).

---

## 📦 Verzeichnisstruktur

```
tiktok-video-automation/
├── short_create.py          # Haupt-Skript
├── yt_sc.py                 # YouTube-Download-Modul
├── VoiceRSSWebAPI.py        # Text-to-Speech API
├── settings.json            # Konfiguration + API-Keys
├── requirements.txt         # Python-Dependencies
├── build.sh                 # Setup-Skript
├── SETUP.md                 # Diese Anleitung
└── video_audio/             # Output-Verzeichnis
    ├── final_tiktok_video.mp4
    ├── story_audio.mp3
    └── hookaudio.mp3
```

---

## 🎯 Features

- ✅ **2-Part oder 1-Part Videos** (~1 Minute pro Part)
- ✅ **KI-generierte Stories** (Groq/Llama3)
- ✅ **Text-to-Speech** (VoiceRSS, 4 Stimmen)
- ✅ **Wort-für-Wort Untertitel** (Faster-Whisper)
- ✅ **Automatischer Hintergrund-Download** (YouTube)
- ✅ **Watermark** (anpassbar)
- ✅ **TikTok-Format** (720x1280, 9:16)
- ✅ **CPU-kompatibel** (kein GPU benötigt)

---

## 📄 Lizenz

Projekt von [@francool57](https://github.com/francool57)

Angepasst von @kavalier_cc
