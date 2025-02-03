import requests
import json
from shared_info import SharedInfo
from utils.translator import translate_to_korean


def getArtistsInfo(artist):
    print(f"\nCurrent Artist Name : {artist}\n")
    url = f'https://ws.audioscrobbler.com/2.0/'
    params = {
        'method': 'artist.getinfo',
        'artist': artist,
        'api_key': SharedInfo.get_api_key(),
        'format': 'json',
    }
    response = requests.get(url, params=params)
    if(response.status_code == 200):
        artist_profile = response.json()
        # print(json.dumps(response_json, sort_keys=True, indent=4))
        artist_name = artist_profile['artist']['name']
        
        # musicbrainz search
        url = f'https://musicbrainz.org/ws/2/artist'
        params = {
            'query': artist_name,
            'limit': 1,
            'fmt': 'json',
        }
        response = requests.get(url, params=params)
        
        mbid = None
        if(response.status_code == 200):
            artist_meta_data = response.json()
            # print(json.dumps(response_json, sort_keys=True, indent=4))
            mbid = artist_meta_data['artists'][0]['id']
            print("%s : %s" % (artist_name, mbid))

        bio = artist_profile['artist']['bio']['content']
        
        # @@@@@@@ 장르(tag)는 last.fm이 나을듯.
        
        # Translate to Korean
        # artist_name_kr = translate_to_korean(artist_name)
        # bio_kr = translate_to_korean(bio)


        # --------insert into artist_tb---------
        # exists
                # return artist id
            # not exists
                # insert
                # parameter: artist_name, bio, mbid
                # return artist id
        # return artist id

        # for tag in response_json['artist']['tags']['tag']:
        #     tag_en = tag['name']
            # tag_kr = translate_to_korean(tag['name'])
            
            # --------insert into genre_tb--------
            # exists
                # return genre id
            # not exists
                # insert
                # parameter: genre_en, genre_kr
                # return genre id

            # --------insert to artist_genre_tb--------
            # parameter: artist_id, genre_id
        # return artist_id
        # return {'insert_id' : 1, 'artist_mbid' : mbid}
            
    else:
        print("Get info error!")