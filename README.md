# Spotify → YouTube Playlist Sync

A Python Flask web application that automatically creates a **private YouTube playlist** from a user’s **Spotify liked songs** using official APIs and OAuth 2.0 authentication.

This project does **not** download or redistribute media — it only links existing YouTube videos into a playlist.

---

## Features
- OAuth 2.0 authentication with **Spotify** and **YouTube**
- Reads a user’s Spotify liked songs
- Searches YouTube for matching videos
- Creates a private YouTube playlist and adds matching tracks
- Secure session-based token handling
- Environment-variable configuration (no hardcoded secrets)

---

## Tech Stack
- **Backend:** Python, Flask  
- **APIs:** Spotify Web API, YouTube Data API v3  
- **Authentication:** OAuth 2.0 (Spotipy, Google Auth libraries)  
- **Version Control:** Git, GitHub  

---

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/spotify-to-youtube-playlist.git
cd spotify-to-youtube-playlist
2. Create and activate a virtual environment
python -m venv .venv

Windows

.\.venv\Scripts\Activate.ps1

macOS / Linux

source .venv/bin/activate
3. Install dependencies
pip install -r requirements.txt
Environment Variables

Set the following environment variables before running the app:

SPOTIPY_CLIENT_ID
SPOTIPY_CLIENT_SECRET
SPOTIPY_REDIRECT_URI=http://127.0.0.1:5000/redirect

YOUTUBE_REDIRECT_URI=http://127.0.0.1:5000/youtube/callback
FLASK_SECRET_KEY
OAUTHLIB_INSECURE_TRANSPORT=1   # Local development only

Note: google_client_secret.json (downloaded from Google Cloud OAuth credentials) must be present in the project root and must not be committed to GitHub.

Running the App
python -m flask run --debug

Open in your browser:

http://127.0.0.1:5000/home
Usage Flow

Log in with Spotify

Log in with YouTube

Create a YouTube playlist from Spotify liked songs

Open the generated playlist on YouTube

Notes

Playlists are created as private by default

YouTube API quota limits apply (initial sync is capped for testing)

This project is intended for educational and personal use

Future Improvements

Sync from specific Spotify playlists

Custom playlist names and privacy settings

Improved YouTube matching and caching

Progress indicators during playlist creation