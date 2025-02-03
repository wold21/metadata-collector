import requests
import artist_info
from shared_info import SharedInfo

def getTopArtists():
    LIMIT = 50
    PAGE = 1
    url = f'https://ws.audioscrobbler.com/2.0/'
    params = {
        'method': 'chart.gettopartists',
        'api_key': SharedInfo.get_api_key(),
        'format': 'json',
        'limit': LIMIT,
        'page': PAGE
    }

    response = requests.get(url, params=params)

    if(response.status_code == 200):
        response_json = response.json()
        for artist in response_json['artists']['artist']:
            result = artist_info.getArtistsInfo(artist['name'])
            # print(f"{artist['name']} : {result['insert_id']} : {result['artist_mbid']}")
    else:
        print("Get top artists error!")