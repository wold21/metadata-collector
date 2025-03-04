from shared_info import SharedInfo
from utils.cal_date import parse_incomplete_date
from utils.common_request import get
from utils.database import get_connection, execute_query, fetch_one, fetch_all, insert_data
from utils.logging_config import logger
from store_tracks import insertAlbumTracksTxn
from enum import Enum


class AlbumType(Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"

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

def insertArtistAlbumsTxn(artist_id, artist_name, mbid):
    temp_data = get(SharedInfo.get_musicbrainz_base_url() + "release-group/", params = {
        'artist': mbid,
        'fmt': 'json',
    })

    albums_info = get(SharedInfo.get_musicbrainz_base_url() + "release-group/", params = {
        'artist': mbid,
        'inc': 'genres',
        'limit': temp_data['release-group-count'],
        'fmt': 'json',
    })
    
    logger.info(f"(2) 아티스트 앨범 List >> 아트스트명 : {artist_name} , 총 앨범 수 : {albums_info['release-group-count']}")
    with get_connection() as conn:  
        cnt = 0
        for album in albums_info.get('release-groups', []):
            try:
                album_name = album['title']
                album_relsase_code = album['primary-type'].lower()
                # album_relsase_name = PRIMARY_ALBUM_TYPE_DICT.get(album_relsase_code, '기타')
                release_date = parse_incomplete_date(album.get('first-release-date', ''))
                release_date_origin = album.get('first-release-date', '')

                # DB에서 기존 album_id 조회
                album_id = fetch_one(conn,  "SELECT id FROM album_tb WHERE title = %s AND release_date_origin = %s", (album_name, release_date_origin))
                if album_id:
                    logger.info(f"\t 이미 존재하는 Album : {album_name}\n")    
                    continue

                # insert DB
                album_id = insertAlbum(conn, album_name, release_date, release_date_origin)
                insertArtistAlbum(conn, artist_id, album_id)
                insertAlbumType(conn, album_relsase_code, album_id, AlbumType.PRIMARY.value)

                secondary_album_type_arr = []
                # if secondary type exists
                if 'secondary-types' in album:
                    for type_str in album['secondary-types']:
                        type_en = type_str.lower()
                        secondary_album_type_arr.append(type_en)
                        insertAlbumType(conn, type_en, album_id, AlbumType.SECONDARY.value)
                
                # Step 8: 장르 정보 저장 (genres 데이터 처리 추가)
                genres = album.get('genres', [])
                if not genres:
                    logger.warning(f"앨범 '{album.get('title')}'에 장르 정보가 없습니다 (album_id: {album_id})")
                else:
                    for genre in genres:
                        genre_name = genre['name']

                        # 장르 코드 삽입 및 id 획득
                        genre_id = insertGenre(conn, genre_name)

                        # 앨범-장르 관계 저장
                        insertAlbumGenre(conn, album_id, genre_id)

                    logger.info(f"앨범 장르 정보 저장 완료 (album_id: {album_id})")

                cnt += 1

                logger.info(f"\t{cnt}/{albums_info['release-group-count']} 앨범 정보")
                logger.info(f'\t앨범명: {album_name}')
                logger.info(f'\t발매타입: {album_relsase_code}')
                logger.info(f'\t앨범작업타입: {secondary_album_type_arr}')
                logger.info(f'\t발매일: {release_date}')
                logger.info(f'\t발매일(가공전): {release_date_origin}\n')

                # insertAlbumTracksTxn(artist_name, album_name)

                # TODO
                # 앨범 이미지 다운로드 로직 추가. 
            except Exception as e:
                    logger.error(f"오류 발생 (앨범 데이터 처리 중) {artist_name} : {e}\n")

        
def insertAlbum(conn, title, release_date, release_date_origin):
    query = """
        INSERT INTO album_tb (title, release_date, release_date_origin)
        VALUES (%s, %s, %s)
        RETURNING id
    """
    album_id = insert_data(conn, query, (title, release_date, release_date_origin))
    logger.info(f"(2-1) [DB] >> 앨범 데이터 삽입 완료 (album_id: {album_id}, title: {title})")
    return album_id[0] if album_id else None


def insertAlbumType(conn, album_release_code, album_id, category):
    query = """
        INSERT INTO album_type_tb (release_id, album_id, type_category)
        SELECT id, %s, %s FROM album_release_code WHERE code = %s
        ON CONFLICT DO NOTHING;
    """
    execute_query(conn, query, (album_id, category, album_release_code ))
    logger.info(f"(2-2) [DB] >> 앨범-타입 데이터 삽입 완료 (album_id: {album_id}, category: {category}, album_release_code: {album_release_code})")


def insertArtistAlbum(conn, artist_id, album_id):
    query = """
        INSERT INTO artist_album_tb (artist_id, album_id)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING
    """
    execute_query(conn, query, (artist_id, album_id))
    logger.info(f"(2-3) [DB] >> 앨범-아티스트 데이터 삽입 완료 (album_id: {album_id}, artist_id: {artist_id}")


def insertGenre(conn, code):
    query = """
        WITH ins AS (
            INSERT INTO genre_code (code)
            VALUES (%s)
            ON CONFLICT (code) DO NOTHING
            RETURNING id
        )
        SELECT id FROM ins
        UNION ALL
        SELECT id FROM genre_code WHERE code = %s
        LIMIT 1
    """
    genre_id = insert_data(conn, query, (code, code))
    return genre_id[0]


def insertAlbumGenre(conn, album_id, genre_id):
    query = """
        INSERT INTO album_genre_tb (album_id, genre_id)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING
    """
    execute_query(conn, query, (album_id, genre_id))

# 앨범에 대한 정보
# https://musicbrainz.org/ws/2/release/acbb807b-4a1a-411a-a800-965a23955561?inc=aliases%2Bartist-credits%2Blabels%2Bdiscids%2Brecordings&fmt=json

# 아티스트기준 앨범 정보 조회 후 해당 앨범 mbid로 조회
# musicbrainz의 mbid와 lastfm의 mbid가 상통함
