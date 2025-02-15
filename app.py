import streamlit as st
from transformers import pipeline
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Load the sentiment analysis pipeline from Hugging Face
sentiment_analyzer = pipeline("sentiment-analysis")

# Spotify API credentials (replace with your own)
SPOTIPY_CLIENT_ID = "472760a900424dfeb9cfeeca0f41748a"
SPOTIPY_CLIENT_SECRET = "17b2088c32bc4b5696f3b1603607ce6f"
SPOTIPY_REDIRECT_URI = "http://localhost:8888/callback"

# Authenticate with Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope="playlist-modify-public"
))

# Mood-to-genre mapping
MOOD_TO_GENRE = {
    "POSITIVE": ["pop", "happy", "dance"],
    "NEGATIVE": ["sad", "blues", "acoustic"],
    "NEUTRAL": ["indie", "chill", "ambient"]
}

# Function to create a Spotify playlist
def create_playlist(mood, user_input):
    # Get genres based on mood
    genres = MOOD_TO_GENRE.get(mood, ["pop"])  # Default to pop if mood not found

    # Search for tracks based on genres
    tracks = []
    for genre in genres:
        results = sp.search(q=f"genre:{genre}", type="track", limit=5)
        tracks.extend(results["tracks"]["items"])

    # Create a playlist
    playlist = sp.user_playlist_create(
        user=sp.me()["id"],
        name=f"Mood Playlist: {mood}",
        public=True,
        description=f"Generated based on your mood: {user_input}"
    )

    # Add tracks to the playlist
    track_uris = [track["uri"] for track in tracks]
    sp.playlist_add_items(playlist["id"], track_uris)

    return playlist["external_urls"]["spotify"]

# Streamlit app
def main():
    st.title("Mood-Based Playlist Generator 🎵")
    st.write("Tell me how you're feeling, and I'll create a Spotify playlist for you!")

    # Text input from the user
    user_input = st.text_area("How are you feeling today?")

    # Analyze button
    if st.button("Generate Playlist"):
        if user_input:
            # Perform sentiment analysis
            result = sentiment_analyzer(user_input)
            mood = result[0]['label']
            score = result[0]['score']

            # Display mood and confidence
            st.write(f"**Detected Mood:** {mood} (Confidence: {score:.2f})")

            # Create and display the playlist
            st.write("🎧 Generating your playlist...")
            playlist_url = create_playlist(mood, user_input)
            st.success(f"🎉 Your playlist is ready! [Open in Spotify]({playlist_url})")
        else:
            st.warning("Please tell me how you're feeling!")

# Run the app
if __name__ == "__main__":
    main()