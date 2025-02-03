import requests
import json
from utils.cal_date import parse_incomplete_date
from shared_info import SharedInfo

PRIMARY_ALBUM_TYPE_DICT = {
    'album': '정규앨범',
    'single': '싱글',
    'ep': 'EP',
    'broadcast': '방송',
    'other': '기타'
}
SECONDARY_ALBUM_TYPE_DICT = {
    'audiobook' : '오디오북',
    'audio drama' : '오디오 드라마',
    'compilation' : '컴필레이션',
    'demo': '데모',
    'dj' : '디제이',
    'field' : '필드',
    'interview' : '인터뷰',
    'live' : '라이브',
    'bootleg': '부트렉',
    'concert recording': '콘서트 레코딩',
    'mixtape' : '믹스테잎',
    'mixtape/street': '믹스테잎/스트릿',
    'remix' : '리믹스',
    'soundtrack' : '사운드트랙',
    'spokenword' : '스포큰워드',
    'other': '기타'
}

def getTopAlbums():
    # url = f'https://ws.audioscrobbler.com/2.0/'
    url = f'https://musicbrainz.org/ws/2/release-group/'
    # params = {
    #     'method': 'artist.getTopAlbums',
    #     'mbid': '381086ea-f511-4aba-bdf9-71c753dc5077',
    #     'api_key': SharedInfo.get_api_key(),
    #     'format': 'json',
    #     'limit': 1
    # }
    params = {
        'artist': 'f27ec8db-af05-4f36-916e-3d57f91ecf5e',
        'fmt': 'json',
    }

    response = requests.get(url, params=params)

    if(response.status_code == 200):
        response_json = response.json()
        params.update({'limit': response_json['release-group-count']})
        response = requests.get(url, params=params)
        if(response.status_code == 200):
            response_json = response.json()
            # print(json.dumps(response_json, sort_keys=True, indent=4))
            for album in response_json['release-groups']:
                album_name = album['title']
                primary_album_type_en = album['primary-type'].lower()
                primary_album_type_kr = ALBUM_TYPE_DICT[album['primary-type'].lower()]

                primary_album_type = {
                    'en': primary_album_type_en,
                    'kr': primary_album_type_kr
                }
                secondary_album_type_arr = []
            
                # if secondary type exists
                if 'secondary-types' in album:
                    for type_str in album['secondary-types']:
                        type_en = type_str.lower()
                        type_kr = ALBUM_TYPE_DICT[type_en]
                        secondary_album_type_arr.append({
                            'en': type_en,
                            'kr': type_kr
                        })
                release_date = parse_incomplete_date(album['first-release-date'])
                release_date_origin = album['first-release-date']

                # print(album_name)
                # print(primary_album_type)
                # print(secondary_album_type_arr)
                # print(release_date)
                # print(release_date_origin)
                # print(f'\n')


                # --------insert into album_release_code--------
                # exists
                    # return album_type_id
                # not exists
                    # insert
                    # parameter: primary_album_type_en, primary_album_type_kr
                    # return album_type_id

                # --------insert into album_tb--------
                # exists
                    # pass
                # not exists
                    # insert
                    # parameter: album_name, artist_id, release_date

                # --------insert into album_type_tb-------- 

    else:
        print("Get top artists error!")



# 앨범에 대한 정보
# https://musicbrainz.org/ws/2/release/acbb807b-4a1a-411a-a800-965a23955561?inc=aliases%2Bartist-credits%2Blabels%2Bdiscids%2Brecordings&fmt=json

# 아티스트기준 앨범 정보 조회 후 해당 앨범 mbid로 조회
# musicbrainz의 mbid와 lastfm의 mbid가 상통함