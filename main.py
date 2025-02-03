from shared_info import SharedInfo
import top_artists
import artist_info
import top_albums
# APIKEY = "a2540255f09a4e673d2adea41e633d10"

def start():
    print("Scrapper started!")
    # artist_name = top_artists.getTopArtists()
    top_artists.getTopArtists()
    # result = artist_info.getArtistsInfo(artist_name)
    # print(f"{artist_name} : {result['insert_id']} : {result['artist_mbid']}")
    # top_albums.getTopAlbums()


if __name__ == "__main__":
    SharedInfo.set_api_key("a2540255f09a4e673d2adea41e633d10")
    start()