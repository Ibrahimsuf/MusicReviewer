import os

from flask import (
    Flask,
    render_template,
    session,
    request,
    redirect,
    url_for,
    flash,
)

from spotipy import Spotify, CacheHandler
from spotipy.oauth2 import SpotifyOAuth
from utils import get_top_artists, get_ai_judgment
import json

SPOITFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")


class CacheSessionHandler(CacheHandler):
    def __init__(self, session, token_key):
        self.token_key = token_key
        self.session = session

    def get_cached_token(self):
        return self.session.get(self.token_key)

    def save_token_to_cache(self, token_info):
        self.session[self.token_key] = token_info
        session.modified = True


app = Flask(__name__)
app.secret_key = "DEV"
oauth_manager = SpotifyOAuth(
    client_id=SPOITFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri="http://localhost:5000",
    scope="user-top-read",
    cache_handler=CacheSessionHandler(session, "spotify_token"),
    show_dialog=True,
)


@app.route("/")
def homepage():
    session.pop("spotify_token", None)
    if request.args.get("code"):
        oauth_manager.get_access_token(request.args.get("code"))
    
    logged_in = oauth_manager.validate_token(oauth_manager.get_cached_token())
    return render_template(
        "index.html", spotify_auth_url=oauth_manager.get_authorize_url(), logged_in=logged_in
    )


@app.route("/spotify-info", methods=["GET", "POST"])
def show_spotify_info():
    data = request.form
    time_period_map = {"short_term": "Past Week", "medium_term": "Past Month", "long_term": "Past Year"}
    return render_template("show_spotify_info.html", time_period=data["time_period"] if data else "long_term", time_period_words=time_period_map[data["time_period"] if data else "Past Year"])

@app.route("/ai_judgment", methods=["POST"])
def ai_judgment():
    if not oauth_manager.validate_token(oauth_manager.get_cached_token()):
        flash("You need to log in to spotify first")
        return redirect("/")
    
    data = request.json
    sp = Spotify(auth_manager=oauth_manager)
    toptracks_text, toptracks_list = get_top_artists(sp, time_range=data["time_period"] if data else "long_term")
    ai_judgment = get_ai_judgment(toptracks_text)
    return json.dumps({"judgment": ai_judgment, "toptracks": toptracks_list})



if __name__ == "__main__":
    app.run(debug=True, use_reloader=True, use_debugger=True)
