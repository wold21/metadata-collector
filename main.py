from shared_info import SharedInfo
import top_artists
import artist_info
import top_albums
# APIKEY = "a2540255f09a4e673d2adea41e633d10"

def start():
    top_artists.getTopArtists()


if __name__ == "__main__":
    SharedInfo.set_api_key("a2540255f09a4e673d2adea41e633d10")
    SharedInfo.set_lastfm_base_url('https://ws.audioscrobbler.com/2.0/')
    SharedInfo.set_musicbrainz_base_url('https://musicbrainz.org/ws/2/')
    start()