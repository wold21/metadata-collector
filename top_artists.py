from utils.common_request import get
import artist_info
import top_albums
from shared_info import SharedInfo

def getTopArtists():
    LIMIT = 1
    TOTAL_PAGE = None
    response_json = get(SharedInfo.get_lastfm_base_url(), params = {
        'method': 'chart.gettopartists',
        'api_key': SharedInfo.get_api_key(),
        'format': 'json',
        'limit': LIMIT,
        'page': 1
    })
    
    TOTAL_PAGE = int(response_json['artists']['@attr']['totalPages'])
    
    for page in range(1, TOTAL_PAGE+1):
        response_json = get(SharedInfo.get_lastfm_base_url(), params = {
            'method': 'chart.gettopartists',
            'api_key': SharedInfo.get_api_key(),
            'format': 'json',
            'limit': LIMIT,
            'page': 1
        })
        
        for artist in response_json['artists']['artist']:
            artist_result = artist_info.getArtistsInfo(artist['name'])
            album_result = top_albums.getTopAlbums(artist_result['artist_id'], artist['name'], artist_result['artist_mbid'])
            