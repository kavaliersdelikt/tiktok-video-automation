import random
import shutil
import os
import requests
from youtubesearchpython import VideosSearch
from yt_dlp import YoutubeDL

class Bcolors: # For colored messages 
    PINK = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

AD_KEYWORDS = {
    'ad', 'advert', 'advertisement', 'sponsor', 'sponsored', 'promo', 'commercial',
    'official trailer', 'trailer', 'launch', 'campaign', 'chromecast', 'google tv',
    'shorts', 'short', 'preroll'
}


def _parse_duration_to_seconds(duration_str):
    if not duration_str:
        return None
    parts = duration_str.split(':')
    try:
        parts = [int(p) for p in parts]
    except ValueError:
        return None
    seconds = 0
    for p in parts:
        seconds = seconds * 60 + p
    return seconds


def _is_ad_result(item):
    """Filter out ads, live streams, shorts, promos, and too-short clips."""
    title = (item.get('title') or '').lower()
    link = item.get('link', '')
    duration_str = item.get('duration')
    duration_s = _parse_duration_to_seconds(duration_str)

    if item.get('type') and item.get('type') != 'video':
        return True
    if item.get('isLive'):
        return True
    if any(key in title for key in AD_KEYWORDS):
        return True
    if '/shorts/' in link:
        return True
    if duration_s is not None and duration_s < 60:
        return True
    return False


# search the video and try to avoid sponsored/advert content
def link_gen(search):
    videosSearch = VideosSearch(search)
    pages_checked = 0

    while pages_checked < 6:
        try:
            results = videosSearch.result().get('result', [])
        except Exception:
            results = []

        filtered = [r for r in results if not _is_ad_result(r) and 'link' in r]
        if filtered:
            choice = random.choice(filtered[: min(len(filtered), 10)])
            print(f'{Bcolors.GREEN}Youtube video was found{Bcolors.END}')
            return choice['link']

        # Advance to next page and try again
        try:
            videosSearch.next()
        except Exception:
            break
        pages_checked += 1

    # If nothing suitable found, fall back to curated list to avoid ads
    fb = random.choice(FALLBACK_URLS)
    print(f"{Bcolors.YELLOW}No clean search result found; using fallback background{Bcolors.END}")
    return fb

def Download(search = 'minecraft parkour gameplay no copyright 4k', url = None, resolution = '1080p', use_curated_first = True):
    # Prefer provided URL, else pick curated fallback first to avoid ads
    if url:
        video_url = url
    elif use_curated_first and FALLBACK_URLS:
        video_url = random.choice(FALLBACK_URLS)
        print(f"{Bcolors.BLUE}Using curated background (no ads){Bcolors.END}")
    else:
        video_url = link_gen(search)

    ydl_opts = {
        'outtmpl': 'fullyoutube.mp4',
        'format': f"bestvideo[height<=1080]+bestaudio/best[height<=1080]",
        'merge_output_format': 'mp4',
        'quiet': True,
        'noplaylist': True,
        'retries': 3,
        'nocheckcertificate': True,
        'http_headers': {'User-Agent': 'Mozilla/5.0'},
        'extractor_args': {'youtube': ['player_client=android']},
    }

    # If user provides cookies.txt in repo root, use it to bypass YouTube bot checks
    cookie_path = os.path.join(os.getcwd(), 'cookies.txt')
    if os.path.exists(cookie_path):
        ydl_opts['cookiefile'] = cookie_path
        print(f"{Bcolors.BLUE}Using cookies.txt for YouTube download{Bcolors.END}")

    # Try primary URL
    if download_with_ytdlp(video_url, ydl_opts):
        return

    # Try another search result if url was auto-picked
    if url is None:
        alt_url = link_gen(search)
        if alt_url != video_url and download_with_ytdlp(alt_url, ydl_opts):
            return

    # Try curated Minecraft fallback URLs
    for fb in FALLBACK_URLS:
        if download_with_ytdlp(fb, ydl_opts):
            return

    # Try local fallback file if present
    if os.path.exists('video_audio/background.mp4'):
        shutil.copy('video_audio/background.mp4', 'fullyoutube.mp4')
        print(f"{Bcolors.GREEN}Used local fallback video_audio/background.mp4{Bcolors.END}")
        return

    # Last resort: download public sample
    download_fallback_sample()


def download_with_ytdlp(video_url, ydl_opts):
    try:
        print(f'{Bcolors.PINK}Downloading with yt-dlp...{Bcolors.END}')
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        print(f"{Bcolors.GREEN}Download was completed{Bcolors.END}")
        return True
    except Exception as e:
        print(f"{Bcolors.RED}yt-dlp failed: {e}{Bcolors.END}")
        return False

def download_fallback_sample():
    # Public domain sample clip (~2m) as a safe last resort (not Minecraft)
    fallback_url = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4"
    target = "fullyoutube.mp4"
    print(f"{Bcolors.PINK}Downloading fallback sample clip...{Bcolors.END}")
    try:
        with requests.get(fallback_url, stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(target, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
        print(f"{Bcolors.GREEN}Fallback sample download completed{Bcolors.END}")
    except Exception as e:
        print(f"{Bcolors.RED}Fallback sample download failed: {e}{Bcolors.END}")


# Curated fallback Minecraft URLs (public/CC sources; availability can vary)
FALLBACK_URLS = [
    "https://archive.org/download/minecraft-parkour-gameplay-2023/minecraft-parkour-gameplay-2023.mp4",
    "https://archive.org/download/minecraft-parkour_202112/minecraft-parkour_202112.mp4",
    "https://archive.org/download/minecraft-parkour-parkour/Minecraft%20Parkour%20Gameplay.mp4",
]