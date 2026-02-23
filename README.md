# Spotify → YouTube Playlist Sync

A Flask web app that:
- Authenticates with Spotify
- Reads liked songs
- Authenticates with YouTube
- Creates a YouTube playlist and adds matching videos

## Setup
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt