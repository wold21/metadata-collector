import datetime
from shared_info import SharedInfo
from utils.common_request import get
from utils.database import get_connection, fetch_one, insert_data, execute_query
from utils.wikipedia import getWikiSummary
from utils.logging_config import logger
import requests
import json


def insertArtistTxn(artist_name=None, mbid=None):

    logger.info(f"아티스트 '{artist_name}' 데이터 조회 및 저장 시작")
    
    if not mbid and not artist_name:
        logger.warning("artist_name과 mbid 중 하나는 필수입니다.")
        return

    # mbid가 있는 경우, MBID로 아티스트 정보 조회 후 이름 재 세팅
    if mbid:
        response = get(SharedInfo.get_musicbrainz_base_url() + f"artist/{mbid}", params={
            'inc': 'genres+aliases',
            'fmt': 'json'
        })
        artist_info = response
        artist_name = artist_info.get('name')

        if not artist_name:
            logger.warning(f"MBID '{mbid}'에 해당하는 아티스트 정보를 찾을 수 없습니다.")
            return

    else:
        # artist_name만 있는 경우 이름으로 조회
        response = get(SharedInfo.get_musicbrainz_base_url() + "artist/", params={
            'query': f'artist:"{artist_name}"',
            'limit': 5,
            'fmt': 'json'
        })
        artists = response.get('artists', [])

        artist_info = next((a for a in artists if a.get('name', '').lower() == artist_name.lower()), None)

        if not artist_info:
            logger.warning(f"정확 이름 '{artist_name}'에 해당하는 아티스트를 찾을 수 없습니다.")
            return

        mbid = artist_info['id']

    logger.info(f"아티스트 '{artist_name}' 데이터 조회 및 저장 시작 (MBID: {mbid})")
    try:
        with get_connection() as conn:
            artist_id = fetch_one(conn, "SELECT id FROM artist_tb WHERE mbid = %s", (mbid,))
            if artist_id:
                logger.info(f"이미 존재하는 아티스트: {artist_name} (MBID: {mbid})")
                return {'artist_id': artist_id, 'artist_name': artist_name, 'artist_mbid': mbid}

            country = artist_info.get('country')
            bio = getWikiSummary(artist_name)
            
            alias_names = {alias['name'].strip() for alias in artist_info.get('aliases', []) if 'name' in alias}
            search_vector = " ".join(sorted({artist_name.strip()} | alias_names))

            # 아티스트 이미지 다운로드 로직 추가. 
            profile_path = get_artist_image(mbid)

            artist_id = insertArtist(conn, artist_name, mbid, country, bio, search_vector, profile_path)
            
            # 엘라스틱 서치 색인 작업
            index_artist_to_elasticsearch(artist_id, artist_name, search_vector)


            for genre in artist_info.get('genres', []):
                genre_id = insertGenre(conn, genre['name'])
                insertArtistGenre(conn, artist_id, genre_id)

            logger.info(f"아티스트 '{artist_name}' 데이터 저장 완료 (ID: {artist_id} / MBID: {mbid})")
            return {'artist_id': artist_id, 'artist_name': artist_name, 'artist_mbid': mbid}

    except Exception as e:
        logger.error(f"오류 발생 (아티스트 데이터 처리 중) : {e}")


def get_artist_image(mbid):
    """TheAudioDB API를 사용해 아티스트 이미지 가져오기"""
    try:
        response = get(SharedInfo.get_theaudiodb_base_url() + SharedInfo.get_theaudiodb_api_key() + "/artist-mb.php",
            params={"i": mbid}
        )
        if not response:  
            logger.warning(f"[TheAudioDB] 응답 없음: {mbid}")
            return None
        if response and "artists" in response and response["artists"]:
            artist_image = response["artists"][0].get("strArtistThumb")
            if artist_image:
                logger.info(f"[TheAudioDB] 아티스트 이미지 URL: {artist_image}")
                return artist_image
        return None
    except Exception as e:
        logger.warning(f"TheAudioDB 이미지 조회 실패 (MBID: {mbid}): {e}")
        return None

def insertArtist(conn, artist_name, mbid, country, bio, search_vector, profile_path):
    query = """
        INSERT INTO artist_tb (artist_name, mbid, country, bio, search_vector, profile_path)
        VALUES (%s, %s, %s, %s, to_tsvector(%s), %s)
        RETURNING id
    """
    artist_id = insert_data(conn, query, (artist_name, mbid, country, bio, search_vector, profile_path))
    logger.info(f"아티스트 데이터 삽입 완료 (artist_id: {artist_id[0]})")
    return artist_id[0]

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


def insertArtistGenre(conn, artist_id, genre_id):
    query = """
        INSERT INTO artist_genre_tb (artist_id, genre_id)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING
    """
    execute_query(conn, query, (artist_id, genre_id))

def index_artist_to_elasticsearch(artist_id, artist_name, search_vector):
    try:
        es_url = SharedInfo.get_elasticsearch_host() + ":" + str(SharedInfo.get_elasticsearch_port())
        
        current_time = datetime.now().isoformat()
        
        doc = {
            "id": str(artist_id),
            "artist_name": artist_name,
            "search_vector": search_vector,
            "created_at": current_time
        }
        
        response = requests.put(
            f"{es_url}/artists/_doc/{artist_id}",
            headers={"Content-Type": "application/json"},
            data=json.dumps(doc)
        )
        response.raise_for_status()
        
        logger.info(f"엘라스틱서치에 아티스트 '{artist_name}' (ID: {artist_id}) 색인 완료")
    
    except Exception as e:
        logger.error(f"엘라스틱서치 색인 중 오류 발생: {e}")