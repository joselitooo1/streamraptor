from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QProgressBar, QListWidget, QFileDialog, QTabWidget, QListWidgetItem, QTextEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QIcon
from services.yt_dlp_service import YtDlpService
from ui.download_thread import DownloadThread
import requests
import os
import json

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("StreamRaptor")
        self.resize(950, 700)
        self.setMinimumSize(850, 600)
        self.yt_service = YtDlpService()
        self.download_path = os.path.expanduser("~/Downloads/Streamraptor")

        self.tabs = QTabWidget()
        self.init_download_tab()
        self.init_about_tab()
        self.init_history_tab()
        self.setCentralWidget(self.tabs)
        self.active_threads = []

    def init_download_tab(self):
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Collez un lien vidéo ou playlist...")

        self.select_folder_btn = QPushButton("📁 Choisir dossier")
        self.select_folder_btn.clicked.connect(self.select_folder)

        self.analyze_btn = QPushButton("🔍 Analyser")
        self.analyze_btn.clicked.connect(self.analyze_url)

        self.thumbnail = QLabel("Miniature")
        self.thumbnail.setAlignment(Qt.AlignCenter)
        self.thumbnail.setFixedHeight(200)

        self.format_list = QListWidget()
        self.format_list.setSelectionMode(QListWidget.MultiSelection)

        self.download_btn = QPushButton("⬇️ Télécharger la sélection")
        self.download_btn.clicked.connect(self.download_selected)

        self.progress_bar = QProgressBar()

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setFixedHeight(100)

        layout = QVBoxLayout()
        layout.addWidget(self.url_input)
        layout.addWidget(self.select_folder_btn)
        layout.addWidget(self.analyze_btn)
        layout.addWidget(self.thumbnail)
        layout.addWidget(self.format_list)
        layout.addWidget(self.download_btn)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.log_area)

        tab = QWidget()
        tab.setLayout(layout)
        self.tabs.addTab(tab, QIcon("streamraptor/assets/icons/download.png"), "Télécharger")

    def init_history_tab(self):
        self.history_list = QListWidget()
        self.load_history()

        layout = QVBoxLayout()
        layout.addWidget(self.history_list)

        tab = QWidget()
        tab.setLayout(layout)
        self.tabs.addTab(tab, QIcon("streamraptor/assets/icons/folder.png"), "Historique")

    def log(self, text):
        self.log_area.append(f"> {text}")

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Choisir un dossier")
        if folder:
            self.download_path = folder
            self.log(f"Dossier sélectionné : {folder}")

    def analyze_url(self):
        self.format_list.clear()
        url = self.url_input.text().strip()
        if not url:
            self.log("❌ Aucun lien fourni.")
            return
        info = self.yt_service.analyze_url(url)
        self.video_url = url
        self.video_title = info.get("title", "unknown")

        if info["type"] == "video":
            self.log(f"✅ Vidéo détectée : {info['title']}")
            self.formats = info["formats"]
            image = requests.get(info["thumbnail"]).content
            pix = QPixmap()
            pix.loadFromData(image)
            self.thumbnail.setPixmap(pix.scaledToHeight(200))
            for f in self.formats:
                self.format_list.addItem(f["label"])

        elif info["type"] == "playlist":
            self.playlist_entries = info["entries"]
            self.log(f"🎞️ Playlist détectée : {info['title']} ({len(self.playlist_entries)} vidéos)")
            
            for video in self.playlist_entries:
                title = video.get("title", "Sans titre")
                video_id = video.get("id")

                item = QListWidgetItem(title)
                item.setData(Qt.UserRole, video)

                # Générer la miniature depuis l'ID YouTube
                if video_id:
                    thumb_url = f"https://i.ytimg.com/vi/{video_id}/mqdefault.jpg"
                    try:
                        image = requests.get(thumb_url).content
                        pix = QPixmap()
                        pix.loadFromData(image)
                        item.setIcon(QIcon(pix))
                    except:
                        pass  # Ne pas bloquer l'ajout

                self.format_list.addItem(item)


    def download_selected(self):
        selected_items = self.format_list.selectedItems()
        if not selected_items:
            self.log("❌ Aucune sélection.")
            return

        for item in selected_items:
            data = item.data(Qt.UserRole)

            if data:  # Cas playlist
                video_url = f"https://www.youtube.com/watch?v={data['id']}"
                title = data.get("title", "Sans titre")
                format_id = None
            else:  # Cas vidéo simple
                index = self.format_list.row(item)
                video_url = self.video_url
                title = self.video_title
                format_id = self.formats[index]["id"]

            thread = DownloadThread(
                video_url,
                format_id,
                self.yt_service,
                self.download_path,
                title
            )

            # Capture safe avec closure personnalisée
            def build_finished_callback(t, video_title):
                return lambda: (
                    self.active_threads.remove(t),
                    self.log(f"✅ {video_title} téléchargée.")
                )

            thread.progress_changed.connect(self.progress_bar.setValue)
            thread.finished.connect(lambda t=thread, ti=title: self.on_thread_finished(t, ti))
            self.active_threads.append(thread)
            thread.start()


    def load_history(self):
        self.history_list.clear()
        path = os.path.join(self.download_path, "history.json")
        if os.path.exists(path):
            with open(path) as f:
                data = json.load(f)
                for item in data:
                    text = f"{item['title']} ({item['format']}) - {item['filepath']}"
                    self.history_list.addItem(QListWidgetItem(text))

    def on_thread_finished(self, thread, title):
        if thread in self.active_threads:
            self.active_threads.remove(thread)
        self.log(f"✅ {title} téléchargée.")
        self.load_history()

    def init_about_tab(self):
        logo = QLabel()
        logo.setAlignment(Qt.AlignCenter)
        pixmap = QPixmap("streamraptor/assets/icons/video.png").scaled(100, 100, Qt.KeepAspectRatio)
        logo.setPixmap(pixmap)

        title = QLabel("🎬 StreamRaptor")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #e50914;")

        credits = QLabel(
            "Développé avec ❤️ par Vianney\n"
            "Technologies : Python, PySide6, yt-dlp\n"
            "Design Phenix497\n"
            "© 2025 StreamRaptor. Tous droits réservés."
        )
        credits.setAlignment(Qt.AlignCenter)
        credits.setStyleSheet("color: gray;")

        layout = QVBoxLayout()
        layout.addWidget(logo)
        layout.addWidget(title)
        layout.addWidget(credits)

        tab = QWidget()
        tab.setLayout(layout)
        self.tabs.addTab(tab, QIcon("streamraptor/assets/icons/video.png"), "À propos")

