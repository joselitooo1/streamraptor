from setuptools import setup

APP = ['main.py']
DATA_FILES = [
    ('streamraptor/assets/icons', ['streamraptor/assets/icons/download.png', 'streamraptor/assets/icons/video.png', 'streamraptor/assets/icons/background.png', 'streamraptor/assets/icons/folder.png','streamraptor/assets/icons/playlist.png','streamraptor/assets/icons/folder.png']),
    ('streamraptor/ui', ['streamraptor/ui/styles.qss']),
]
OPTIONS = {
    'argv_emulation': True,
    'packages': ['PySide6', 'yt_dlp', 'requests'],
    'resources': DATA_FILES,
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    data_files=DATA_FILES,
)
