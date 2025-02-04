from utils.cal_date import parse_incomplete_date
from shared_info import SharedInfo
from utils.common_request import get

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
    'dj-mix' : '디제이 믹스',
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

def getTopAlbums(artist_id, artist_name, mbid):
    temp_data = get(SharedInfo.get_musicbrainz_base_url() + "release-group/", params = {
        'artist': mbid,
        'fmt': 'json',
    })
    
    albums_info = get(SharedInfo.get_musicbrainz_base_url() + "release-group/", params = {
        'artist': mbid,
        'limit': temp_data['release-group-count'],
        'fmt': 'json',
    })
    
    print(f'아티스트 앨범 정보')
    for album in albums_info['release-groups']:
        album_mbid = album['id']
        album_name = album['title']
        primary_album_type_en = album['primary-type'].lower()
        primary_album_type_kr = PRIMARY_ALBUM_TYPE_DICT[album['primary-type'].lower()]

        primary_album_type = {
            'en': primary_album_type_en,
            'kr': primary_album_type_kr
        }
        secondary_album_type_arr = []
    
        # if secondary type exists
        if 'secondary-types' in album:
            for type_str in album['secondary-types']:
                type_en = type_str.lower()
                type_kr = SECONDARY_ALBUM_TYPE_DICT[type_en]
                secondary_album_type_arr.append({
                    'en': type_en,
                    'kr': type_kr
                })
        release_date = parse_incomplete_date(album['first-release-date'])
        release_date_origin = album['first-release-date']

        
        
        print(f'앨범명: {album_name}')
        print(f'발매타입: {primary_album_type}')
        print(f'앨범작업타입: {secondary_album_type_arr}')
        print(f'발매일: {release_date}')
        print(f'발매일(가공전): {release_date_origin}')
        print(f'\n')

        # TODO
        # 앨범 이미지 다운로드 로직 추가. 

        # --------insert into album_tb--------
        # exists
            # pass
        # not exists
            # insert
            # parameter: album_name, artist_id, release_date, release_date_origin
            # return album_id

        # --------insert into album_release_code--------
        # exists
            # return album_type_id
        # not exists
            # insert
            # parameter: primary_album_type_en, primary_album_type_kr
            # return album_type_id

        # --------insert into album_type_tb-------- 
        # primary & secondary
        # exists
            # return album_type_id
        # not exists
            # insert
            # parameter: album_type_id, album_id, {category}
            # return album_type_id
        
        
        # --------insert into artist_album_tb--------
        # exsit
            # pass
        # not exists
            # insert
            # parameter: artist_id, album_id
            # return none
            
        # releases_data = get(SharedInfo.get_musicbrainz_base_url() + f'release-group/{release_group_id}', params={
        #     'inc': 'releases',
        #     'fmt': 'json'
        # })
        
        tracks_info = get(SharedInfo.get_lastfm_base_url(), params={
            'method': 'album.getinfo',
            'artist': artist_name,
            'album': album_name,
            'api_key': SharedInfo.get_api_key(),
            'format': 'json'
        })
        
        if tracks_info and 'album' in tracks_info and 'tracks' in tracks_info['album']:
            track_list = tracks_info['album']['tracks']['track']
        
        if not isinstance(track_list, list):
            track_list = [track_list]
            
        print(f'트랙 정보')
        for track in track_list:
            track_name = track['name']
            track_duration = track.get('duration', 0) 
            track_rank = track.get('@attr', {}).get('rank', 1)
            
            #--------insert into track_tb--------
            # exists
                # return None
            # not exists
                # insert
                # parameter: album_id, title, duration, track_rank
                # return None
            
            #--------insert into artist_track_tb--------
            # exists
                # return None
            # not exists
                # insert
                # parameter: artist_id, track_id
                # return None
            print(f'트랙명: {track_name}')
            print(f'트랙길이: {track_duration}')
            print(f'트랙순위: {track_rank}')
            print(f'\n')
            
        
        



# 앨범에 대한 정보
# https://musicbrainz.org/ws/2/release/acbb807b-4a1a-411a-a800-965a23955561?inc=aliases%2Bartist-credits%2Blabels%2Bdiscids%2Brecordings&fmt=json

# 아티스트기준 앨범 정보 조회 후 해당 앨범 mbid로 조회
# musicbrainz의 mbid와 lastfm의 mbid가 상통함