# Spotify → YouTube Playlist Sync

A Flask web application that creates a **private YouTube playlist** from a user’s **Spotify liked songs** using OAuth 2.0 and official APIs.

The app authenticates with Spotify and YouTube, reads saved tracks from Spotify, searches YouTube for matching videos, and adds them to a newly created playlist. No media is downloaded or redistributed.

## Tech
- Python, Flask
- Spotify Web API
- YouTube Data API
- OAuth 2.0

## Run Locally
```bash
pip install -r requirements.txt
python -m flask run --debug
```
## Open

http://127.0.0.1:5000/home

## Notes
- Playlists are created as private
- Intended for personal and educational use