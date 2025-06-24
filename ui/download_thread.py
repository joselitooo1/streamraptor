from PySide6.QtCore import QThread, Signal
from downloader.video_handler import create_progress_hook
from datetime import datetime
import os
import json

class DownloadThread(QThread):
    progress_changed = Signal(int)
    finished = Signal()

    def __init__(self, url, format_id, yt_service, path, title):
        super().__init__()
        self.url = url
        self.format_id = format_id
        self.yt_service = yt_service
        self.path = path
        self.title = title

    def run(self):
        os.makedirs(self.path, exist_ok=True)
        hook = create_progress_hook(self.progress_changed.emit)

        try:
            filepath = self.yt_service.download(self.url, self.format_id, hook, self.path)
            self.log_history(self.title, self.url, self.format_id or "best", filepath)
        except Exception as e:
            print(f"Erreur lors du téléchargement de {self.url} : {e}")

        self.finished.emit()

    def log_history(self, title, url, fmt, filepath):
        record = {
            "title": title,
            "url": url,
            "format": fmt,
            "filepath": filepath,
            "timestamp": datetime.now().isoformat()
        }
        path = os.path.join(self.path, "history.json")
        history = []
        if os.path.exists(path):
            with open(path) as f:
                history = json.load(f)
        history.append(record)
        with open(path, "w") as f:
            json.dump(history, f, indent=2)
