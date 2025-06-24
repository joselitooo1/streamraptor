from yt_dlp import YoutubeDL

class MetadataExtractor:
    def __init__(self):
        self.ydl_opts = {
            'quiet': True,
            'skip_download': True,
        }

    def extract_info(self, url):
        with YoutubeDL(self.ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)
