from shared_info import SharedInfo
from utils.common_request import get
from utils.translator import translate_to_korean
from utils.database import get_connection, execute_query, fetch_one, fetch_all, insert_data
from utils.wikipedia import getWikiSummary
from utils.logging_config import logger


def insertArtistTxn(artist_name, mbid):

    try:
        with get_connection() as conn:  
            mbid = mbid or getArtistMbid(artist_name)
            # topartist 데이터 중 mbid가 비어 있는 아티스트 존재 / mbid가 비어 있으면 artist_name으로 조회 
            if not mbid:
                logger.warning(f"아티스트 '{artist_name}'의 MBID를 찾을 수 없습니다.")
                return
                
            logger.info("(1) 아티스트 정보")
            logger.info(f"\tArtist Name : {artist_name}")
            logger.info(f"\tMBID : {mbid}")
            
            # DB에서 기존 artist_id 조회
            artist_id = fetch_one(conn, "SELECT id FROM artist_tb WHERE mbid = %s", (mbid,))
            if artist_id:
                logger.info(f"\t이미 존재하는 Artist : {artist_name}\n")    
                return {'artist_id': artist_id[0], 'artist_name': artist_name, 'artist_mbid' : mbid}
            

            # 아티스트 + 장르 + 아티스트-장르 관계 테이블 트랜잭션
            bio = getWikiSummary(artist_name)
            artist_id = insertArtist(conn, artist_name, mbid, bio)
            # 장르 정보 가져와서 DB에 저장
            artist_genres_data = get(SharedInfo.get_musicbrainz_base_url() + f'artist/{mbid}', params={'inc': 'genres', 'fmt': 'json'})
            for tag in artist_genres_data['genres']:
                tag_en = tag['name']
                logger.info(f"Tag : {tag_en}")

                genre_id = insertGenre(conn, tag_en)
                insertArtistGenre(conn, artist_id, genre_id)
            logger.info(f'\n')
            return {'artist_id' : artist_id, 'artist_name' : artist_name, 'artist_mbid' : mbid}
    except Exception as e:
       logger.error(f"오류 발생 (아티스트 데이터 처리 중) : {e}\n")


def getArtistMbid(artist_name):
    response = get(SharedInfo.get_musicbrainz_base_url() + "artist/", params={
        'query': f'artist:{artist_name}', 'limit': 1, 'fmt': 'json'
    })
    if response and "artists" in response and response["artists"]:
        return response["artists"][0].get("id")
    return None


def insertArtist(conn, artist_name, mbid, bio):
    query = """
        INSERT INTO artist_tb (artist_name, mbid, bio) 
        VALUES (%s, %s, %s) 
        RETURNING id
    """
    artist_id = insert_data(conn, query, (artist_name, mbid, bio))
    logger.info(f"(1-1) [DB] >> 아티스트 데이터 삽입 완료 (artist_id: {artist_id})")
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
    logger.info(f"(1-2) [DB] >> 장르데이터 조회 및 삽입 완료 (genre_id: {genre_id})")
    return genre_id[0]


def insertArtistGenre(conn, artist_id, genre_id):
    query = """
                INSERT INTO artist_genre_tb (artist_id, genre_id)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
            """
    execute_query(conn, query, (artist_id, genre_id))
    logger.info(f"(1-3) [[DB] >> 아티스트-장르 관계 삽입 완료 (Artist ID: {artist_id}, Genre ID: {genre_id})")


