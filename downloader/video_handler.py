import os
from yt_dlp import YoutubeDL

def create_progress_hook(callback):
    def hook(d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            if total:
                percent = int(downloaded * 100 / total)
                callback(percent)
    return hook

class VideoHandler:
    def __init__(self):
        pass

    def download_video(self, url, format_id=None, progress_hook=None, path="."):
        os.makedirs(path, exist_ok=True)

        ydl_opts = {
            'outtmpl': os.path.join(path, '%(title)s.%(ext)s'),
            'format': format_id or 'best',
            'progress_hooks': [progress_hook] if progress_hook else [],
            'quiet': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'
            }
        }

        with YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(result)
