from shared_info import SharedInfo
from utils.cal_date import parse_incomplete_date
from utils.common_request import get
from utils.database import get_connection, execute_query, fetch_one, fetch_all, insert_data, fetch_one_dict
from utils.logging_config import logger

def insertAlbumTracksTxn(artist_name, album_name):
    
    tracks_info = get(SharedInfo.get_lastfm_base_url(), params={
        'method': 'album.getinfo',
        'artist': artist_name,
        'album': album_name,
        'api_key': SharedInfo.get_api_key(),
        'format': 'json'
    })

    with get_connection() as conn:  
        # `artist_tb`에서 artist_id 가져오기
        artist_query = "SELECT id as artist_id, artist_name, mbid FROM artist_tb WHERE artist_name = %s;"
        artist_data = fetch_one_dict(conn, artist_query, (artist_name,))
        if not artist_data:
            logger.warning(f"아티스트 '{artist_name}'의 정보가 존재하지 않음.")
            return
        artist_id = artist_data['artist_id']

        # `album_tb`에서 album_id 가져오기
        album_query = "SELECT id as album_id FROM album_tb WHERE title = %s;"
        album_data = fetch_one_dict(conn, album_query, (album_name,))
        if not album_data:
            logger.warning(f"앨범 '{album_name}'의 정보가 존재하지 않음.")
            return
        album_id = album_data['album_id']

        try:
            if tracks_info and tracks_info.get('album', {}).get('tracks'):
                # ✅ 트랙이 없는 앨범 존재
                # https://ws.audioscrobbler.com/2.0/?method=chart.gettopartists&api_key=a2540255f09a4e673d2adea41e633d10&format=json&limit=1&page=1
                if tracks_info.get('album', {}).get('tracks', {}).get('track', []):

                    logger.info(f"(3) 트랙 List >> 아트스트명 : {artist_name} , 앨범명 : {album_name} , 총 앨범 수 : {len(tracks_info['album']['tracks'])}")
                    track_list = tracks_info['album']['tracks']['track']
                    if not isinstance(track_list, list):
                        track_list = [track_list]

                    cnt = 0
                    for track in track_list:
                        track_name = track['name']
                        track_duration = track.get('duration', 0) 
                        track_rank = track.get('@attr', {}).get('rank', 1)
                        
                        cnt += 1
                        logger.info(f"\t{cnt}/{len(tracks_info['album']['tracks']['track'])} 트랙 정보")
                        logger.info(f'\t트랙명: {track_name}')
                        logger.info(f'\t트랙길이: {track_duration}')
                        logger.info(f'\t트랙순위: {track_rank}\n')

                        track_id = insertTrack(conn, album_id, track_name, track_duration, track_rank)
                        if track_id:
                            insertArtistTrack(conn, artist_id, track_id)
                        else:
                            logger.warning(f"이미 존재하는 트랙 : {track_name}\n")
            else:
                logger.warning(f"(3) 트랙 List \n\t앨범 '{album_name}'의 트랙이 없음\n")
        except Exception as e:
                logger.error(f"오류 발생 (트랙 데이터 처리 중) {artist_name}, {album_name}: {e}\n")
    


def insertTrack(conn, album_id, track_name, track_duration, track_rank):
    query = """
        INSERT INTO track_tb (album_id, track_name, duration, track_rank) 
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (album_id, track_name) DO NOTHING
        RETURNING id;
    """
    track_id = insert_data(conn, query, (album_id, track_name, track_duration, track_rank))
    logger.info(f"(3-1) [DB] >> 트랙 데이터 삽입 완료 (track_id: {track_id})")
    return track_id[0] if track_id else None


def insertArtistTrack(conn, artist_id, track_id):
    query = """
        INSERT INTO artist_track_tb (artist_id, track_id)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING
    """
    execute_query(conn, query, (artist_id, track_id))
    logger.info(f"(3-2) [DB] >> 아티스트-트랙 관계 삽입 완료 (Artist ID: {artist_id}, Track ID: {track_id})")


