from shared_info import SharedInfo
from utils.cal_date import parse_incomplete_date
from utils.common_request import get
from utils.database import get_connection, execute_query, fetch_one, fetch_one_dict, insert_data
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
}
# 제외된 작업타입 (기타, 스포큰워드, 방송, 오디오북, 오디오 드라마, 부트랙)
EXCLUDED_SECONDARY_TYPE_DICT = {'other', 'spokenword', 'broadcast', 'audiobook', 'audio drama', 'bootleg'}

def log_album_info(cnt, total, album_name, release_type, secondary_types, release_date, release_date_origin, reason=None):
    logger.info(f"\t{cnt}/{total} 앨범 정보")
    if reason:
        logger.warning(f"\t앨범 insert 생략")
        logger.warning(f"\t이유: {reason}")
    logger.info(f'\t앨범명: {album_name}')
    logger.info(f'\t발매타입: {release_type}')
    logger.info(f'\t앨범작업타입: {secondary_types}')
    logger.info(f'\t발매일: {release_date}')
    logger.info(f'\t발매일(가공전): {release_date_origin}\n')

def insertArtistAlbumsTxn(mbid):
    base_url = SharedInfo.get_musicbrainz_base_url() + "release-group/"
    limit = 100  # MusicBrainz API는 limit 최대 100

    # 첫 요청: 전체 앨범 개수 + 첫 100개 데이터 가져오기
    first_response = get(base_url, params={
        'artist': mbid,
        'inc': 'genres',
        'limit': limit,
        'fmt': 'json'
    })

    total_albums = first_response.get('release-group-count', 0)
    albums = first_response.get("release-groups", [])
    
    logger.info(f"총 {total_albums}개의 앨범 발견")

    if total_albums > limit:
        offset = limit

        while offset < total_albums:
            response = get(base_url, params={
                'artist': mbid,
                'inc': 'genres',
                'limit': limit,
                'offset': offset,
                'fmt': 'json',
            })
            if "release-groups" in response:
                albums.extend(response["release-groups"])

            offset += limit 

    albums_info = {"release-groups": albums, "release-group-count": total_albums}
    inserted_album_count = 0

    with get_connection() as conn:  
        artist_info = fetch_one_dict(conn, "SELECT id, artist_name, country FROM artist_tb WHERE mbid = %s", (mbid,))
        if not artist_info:
            raise ValueError(f"아티스트 정보를 찾을 수 없습니다. mbid: {mbid}")

        artist_name = artist_info['artist_name']
        artist_country = artist_info['country']
        
        logger.info(f"(2) 아티스트 앨범 List >> 아트스트명 : {artist_name} , 총 앨범 수 : {albums_info['release-group-count']}")

        cnt = 0
        for album in albums_info.get('release-groups', []):
            try:
                cnt += 1

                album_name = album['title']
                album_relsase_code = album['primary-type'].lower()
                
                release_date = parse_incomplete_date(album.get('first-release-date', ''))
                release_date_origin = album.get('first-release-date', '')
                release_groups_id = album['id']
                
                if not release_date_origin:
                    log_album_info(cnt, albums_info['release-group-count'], album_name, album_relsase_code, album['secondary-types'], release_date, release_date_origin, "release_date_origin 없음")
                    continue
                
                if 'secondary-types' in album:
                    if any(type_.lower() in EXCLUDED_SECONDARY_TYPE_DICT for type_ in album['secondary-types']):
                        log_album_info(cnt, albums_info['release-group-count'], album_name, album_relsase_code, album['secondary-types'], release_date, release_date_origin, "제외된 secondary type 포함")
                        continue

                # DB에서 기존 album_id 조회
                album_id = fetch_one(conn,  "SELECT id FROM album_tb WHERE title = %s AND release_date_origin = %s", (album_name, release_date_origin))
                if album_id:
                    logger.warning(f"\t 이미 존재하는 Album : {album_name}\n")    
                    continue

                # 앨범 이미지 다운로드 로직 추가. 
                album_image = get_album_image(release_groups_id)

                # if not album_image:
                    # log_album_info(cnt, albums_info['release-group-count'], album_name, album_relsase_code, album['secondary-types'], release_date, release_date_origin, "앨범 이미지 없음")
                    # continue

                # insert DB
                inserted_album_count += 1 
                album_id = insertAlbum(conn, album_name, release_date, release_date_origin, album_image, release_groups_id)
                insertAlbumType(conn, album_relsase_code, album_id, AlbumType.PRIMARY.value)

                if 'secondary-types' in album:
                    for type_str in album['secondary-types']:
                        type_en = type_str.lower()
                        insertAlbumType(conn, type_en, album_id, AlbumType.SECONDARY.value)
                
                # 장르 정보 저장
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

                log_album_info(cnt, albums_info['release-group-count'], album_name, album_relsase_code, album['secondary-types'], release_date, release_date_origin)

                # Release 리스트 조회
                release_group_id = album['id']
                releases_info = get(SharedInfo.get_musicbrainz_base_url() + f"release-group/{release_group_id}", params = {
                    'inc': 'releases',
                    'fmt': 'json',
                })
                releases = releases_info.get('releases', [])

                priority_order = [
                    ("quality == 'high'", lambda r: r.get('quality') == 'high'),
                    ("status == 'Official' and country == artist_country", lambda r: r.get('status') == 'Official' and r.get('country') == artist_country),
                    ("status == 'Official'", lambda r: r.get('status') == 'Official'),
                    ("country == artist_country", lambda r: r.get('country') == artist_country),
                    ("fallback (no match)", lambda r: True)
                ]
                latest_release = None
                reason = None

                for desc, condition in priority_order:
                    candidates = list(filter(condition, releases))
                    if candidates:
                        latest_release = candidates[0]
                        reason = desc
                        break

                if latest_release:
                    logger.info("• 선택된 release 이유 : {reason}")
                else:
                    logger.error("❌ release를 찾을 수 없습니다.")
    
                # 트랙 리스트 조회
                insertAlbumTracksTxn(latest_release['id'], album_id, mbid)

            except Exception as e:
                    logger.error(f"오류 발생 (앨범 데이터 처리 중) {artist_name} : {e}\n")

        logger.info(f"[앨범 저장 결과] 총 {albums_info['release-group-count']}개 중 {inserted_album_count}개 앨범 insert 완료")
        update_representative_covers(mbid)


def get_album_image(mb_release_group_id):
    """TheAudioDB API를 사용하여 앨범 이미지 가져오기"""
    try:
        response = get(SharedInfo.get_theaudiodb_base_url() + SharedInfo.get_theaudiodb_api_key() + f"/album-mb.php",
            params={"i": mb_release_group_id}
        )
        if not response:  
            logger.warning(f"[TheAudioDB] 응답 없음: {mb_release_group_id}")
            return None
        if "album" in response and response["album"]:
            album_image = response["album"][0].get("strAlbumThumb")
            if album_image:
                logger.info(f"[TheAudioDB] 앨범 이미지 URL: {album_image}")
                return album_image
        return None
    except Exception as e:
        logger.warning(f"TheAudioDB 이미지 조회 실패 (MBID: {mb_release_group_id}): {e}")
        return None
    
    
def insertAlbum(conn, title, release_date, release_date_origin, cover_path, mbid):
    query = """
        INSERT INTO album_tb (title, release_date, release_date_origin, cover_path, mbid)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """
    album_id = insert_data(conn, query, (title, release_date, release_date_origin, cover_path, mbid))
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


def update_representative_covers(mbid):
    query = """
        WITH representative_cover AS (
            SELECT 
                TRIM(SPLIT_PART(at.title, '(', 1)) AS base_title,
                at.cover_path
            FROM album_tb at
            JOIN artist_album_tb aat ON at.id = aat.album_id
            JOIN artist_tb ar ON ar.id = aat.artist_id
            WHERE at.cover_path IS NOT NULL AND ar.mbid = %s
        ),
        target_albums AS (
            SELECT 
                at.id,
                TRIM(SPLIT_PART(at.title, '(', 1)) AS base_title
            FROM album_tb at
            JOIN artist_album_tb aat ON at.id = aat.album_id
            JOIN artist_tb ar ON ar.id = aat.artist_id
            WHERE at.cover_path IS NULL AND ar.mbid = %s
        )
        UPDATE album_tb target
        SET cover_path = rep.cover_path
        FROM representative_cover rep
        JOIN target_albums ta ON ta.base_title = rep.base_title
        WHERE target.id = ta.id;

    """

    with get_connection() as conn:
        updated_rows = execute_query(conn, query, (mbid, mbid))
        logger.info(f"[DB] >> 대표 이미지 없는 앨범들의 cover_path {updated_rows}건 업데이트 완료 (artist mbid: {mbid})")
