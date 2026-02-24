from flask import Flask, request, url_for, session, redirect, render_template
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

app = Flask(__name__)

app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-only-secret")
app.config['SESSION_COOKIE_NAME'] = 'Brandons Cookie'
TOKEN_INFO = "token_info"
YOUTUBE_TOKEN_INFO = "youtube_token_info"
YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube"]
GOOGLE_CLIENT_SECRETS_FILE = "google_client_secret.json"

@app.route("/home")
def home():
    spotify_ok = TOKEN_INFO in session
    youtube_ok = YOUTUBE_TOKEN_INFO in session
    return render_template("home.html", spotify_ok=spotify_ok, youtube_ok=youtube_ok)

@app.route("/")
def index():
    return redirect(url_for("home"))

@app.route("/spotify/login")
def spotify_login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/redirect')
def redirectPage():
    sp_oauth = create_spotify_oauth()
    session.pop(TOKEN_INFO, None)
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('youtube_login', _external=True))

@app.route('/getTracks')
def getTracks():
    try:
        token_info = get_token()
    except:
        print("user not logged in")
        return redirect("/")
    sp = spotipy.Spotify(auth=token_info['access_token'])
    all_songs = []
    iter = 0
    while True:
        items = sp.current_user_saved_tracks(limit = 50, offset = iter * 50)['items']
        iter += 1
        all_songs += items
        if len(items) < 50:
            break
    return str(len(all_songs))

@app.route("/youtube/login")
def youtube_login():
    # Require Spotify first
    if TOKEN_INFO not in session:
        return redirect(url_for("spotify_login", _external=True))

    flow = create_youtube_flow()
    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )
    session["youtube_oauth_state"] = state
    return redirect(auth_url)

@app.route("/youtube/callback")
def youtube_callback():
    state = session.get("youtube_oauth_state")
    if not state:
        return "Missing OAuth state. Try /youtube/login again.", 400

    flow = create_youtube_flow(state=state)
    flow.fetch_token(authorization_response=request.url)

    creds = flow.credentials
    session[YOUTUBE_TOKEN_INFO] = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes,
    }
    if TOKEN_INFO not in session:
        return redirect(url_for("spotify_login", _external=True))
    
    return redirect(url_for("sync_page"))

@app.route("/sync", methods=["GET", "POST"])
def sync_page():
    if request.method == "GET":
        return redirect(url_for("home"))

    # read form inputs
    title = request.form.get("title", "Spotify Liked Songs (Auto)").strip()
    privacy = request.form.get("privacy", "private").strip()
    limit = request.form.get("limit", "25").strip()

    try:
        limit = max(1, min(200, int(limit)))
    except:
        limit = 25

    # Require both auth
    if TOKEN_INFO not in session:
        return redirect(url_for("spotify_login", _external=True))
    if YOUTUBE_TOKEN_INFO not in session:
        return redirect(url_for("youtube_login", _external=True))

    # Spotify
    token_info = get_token()
    sp = spotipy.Spotify(auth=token_info["access_token"])
    track_queries = get_saved_track_queries(sp)[:limit]

    # YouTube
    yt = youtube_service()

    # Create playlist
    playlist = yt.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {"title": title, "description": "Created from Spotify liked songs"},
            "status": {"privacyStatus": privacy},
        }
    ).execute()
    playlist_id = playlist["id"]

    # Search + add
    added = 0
    skipped = 0
    for q in track_queries:
        search = yt.search().list(
            part="snippet",
            q=q,
            type="video",
            maxResults=1
        ).execute()

        items = search.get("items", [])
        if not items:
            skipped += 1
            continue

        video_id = items[0]["id"]["videoId"]
        yt.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {"kind": "youtube#video", "videoId": video_id},
                }
            }
        ).execute()
        added += 1

    playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
    spotify_ok = True
    youtube_ok = True
    return render_template(
        "result.html",
        spotify_ok=spotify_ok,
        youtube_ok=youtube_ok,
        playlist_id=playlist_id,
        playlist_url=playlist_url,
        added=added,
        skipped=skipped
    )

def get_saved_track_queries(sp):
    queries = []
    offset = 0
    while True:
        resp = sp.current_user_saved_tracks(limit=50, offset=offset)
        items = resp.get("items", [])
        for it in items:
            track = it["track"]
            title = track["name"]
            artists = ", ".join(a["name"] for a in track["artists"])
            queries.append(f"{title} {artists}")
        if len(items) < 50:
            break
        offset += 50
    return queries

def create_youtube_flow(state=None):
    return Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE,
        scopes=YOUTUBE_SCOPES,
        redirect_uri=os.getenv("YOUTUBE_REDIRECT_URI"),
        state=state,
    )

def get_youtube_credentials():
    data = session.get(YOUTUBE_TOKEN_INFO)
    if not data:
        raise RuntimeError("YouTube not logged in")
    return Credentials(**data)

def youtube_service():
    creds = get_youtube_credentials()
    return build("youtube", "v3", credentials=creds)

def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        raise RuntimeError("Spotify not logged in")
    now = int(time.time())

    is_expired = token_info['expires_at'] - now < 60
    if (is_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        session[TOKEN_INFO] = token_info
    return token_info

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        scope="user-library-read",
        show_dialog=True
    )