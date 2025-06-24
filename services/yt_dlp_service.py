from downloader.metadata_extractor import MetadataExtractor
from downloader.video_handler import VideoHandler
from downloader.formats import extract_format_options

class YtDlpService:
    def __init__(self):
        self.extractor = MetadataExtractor()
        self.handler = VideoHandler()

    def analyze_url(self, url):
        info = self.extractor.extract_info(url)
        if 'entries' in info:
            # C'est une playlist
            return {
                "type": "playlist",
                "title": info.get("title"),
                "entries": info.get("entries", [])
            }
        else:
            # C'est une vidéo seule
            formats = extract_format_options(info.get("formats", []))
            return {
                "type": "video",
                "title": info.get("title"),
                "thumbnail": info.get("thumbnail"),
                "formats": formats,
            }

    def download(self, url, format_id=None, hook=None, path="."):
        return self.handler.download_video(
            url,
            format_id=format_id,
            progress_hook=hook,
            path=path
        )
