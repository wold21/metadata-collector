from shared_info import SharedInfo
from utils.common_request import get
from utils.translator import translate_to_korean


def getArtistsInfo(artist):
    print("---------------------------------------")
    mbid = None
    artist_profile = get(SharedInfo.get_lastfm_base_url(), params = {
        'method': 'artist.getinfo',
        'artist': artist,
        'api_key': SharedInfo.get_api_key(),
        'format': 'json',
    })
    
    artist_name = artist_profile['artist']['name']
    
    # musicbrainz search
    artist_meta_data = get(SharedInfo.get_musicbrainz_base_url() + "artist/", params = {
        'query': artist_name,
        'limit': 1,
        'inc': 'genres',
        'fmt': 'json',
    })

    mbid = artist_meta_data['artists'][0]['id']
    print("%s : %s" % (artist_name, mbid))

    bio = artist_profile['artist']['bio']['content']
    
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
    
    print("아티스트 정보")
    print(f"Artist Name : {artist_name}")
    print(f"Bio : {bio[:10]}....")
    print(f"MBID : {mbid}")
    print(f'\n')
    
    
    artist_genres_data = get(SharedInfo.get_musicbrainz_base_url() + f'artist/{mbid}' , params = {
        'inc': 'genres',
        'fmt': 'json',
    })

    print("아티스트 장르 정보")
    for tag in artist_genres_data['genres']:
        tag_en = tag['name']
        # tag_kr = translate_to_korean(tag['name'])
        print(f"Tag : {tag_en}")
        
        # --------insert into genre_tb--------
        # exists
            # return genre id
        # not exists
            # insert
            # parameter: genre_en
            # return genre id

        # --------insert to artist_genre_tb--------
        # parameter: artist_id, genre_id
    # return artist_id
    print(f'\n')
    return {'artist_id' : 1, 'artist_mbid' : mbid}