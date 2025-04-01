from shared_info import SharedInfo
from utils.cal_date import parse_incomplete_date
from utils.common_request import get
from utils.database import get_connection, execute_query, fetch_one, fetch_all, insert_data, fetch_one_dict
from utils.logging_config import logger
import store_artist

NORMALIZED_JOINPHRASE = {
    "and": "and",
    ", and": "and", 
    ",": "and", 
    "&": "and", 
    "+": "and",
    "x": "and",
    "\u00d7": "and",
    
    "with": "with",
    "duet with": "with",
    "meets": "with",

    "feat": "feat",
    "feat.": "feat",
    "feat:": "feat",
    "featuring": "feat",
    "ft": "feat",
    "ft.": "feat",
    "f/": "feat",
    ") feat.": "feat",
    ", feat.": "feat",
    "- feat.": "feat",
    "presentan": "feat",
    "presents": "feat",
    "starring": "feat",
    "sung by": "feat",
    "/": "feat",
    ";": "feat",
    "(": "feat",
    ")": "feat",

    "vs.": "vs",
    "vs": "vs",

    "main": "main"
}

def normalize_joinphrase(joinphrase):
    return NORMALIZED_JOINPHRASE.get(joinphrase.strip().lower(), "feat")

def insertAlbumTracksTxn(release_id, album_id, mbid):

    # 트랙 리스트 조회
    tracks_info = get(SharedInfo.get_musicbrainz_base_url() + f"release/{release_id}", params={
        'inc': 'recordings',
        'fmt': 'json'
    })

    tracks = tracks_info.get('media', [{}])[0].get('tracks', [])
    logger.info(f"(3) 트랙 List >> 앨범 ID : {album_id} , 총 트랙 수 : {len(tracks)}")

    with get_connection() as conn:  
        feat_artists = {}
        for track in tracks:
            track_name = track['title']
            track_duration = track.get('recording', {}).get('length')  # Track length in ms
            track_rank = track.get('position')

            track_id = insertTrack(conn, album_id, track_name, track_duration, track_rank)
            
            # track_id가 None인 경우 로그 찍고 다음 트랙으로 넘어가기
            if not track_id:
                logger.warning(f"\t 이미 존재하는 트랙 Album : album_id={album_id}, track_name={track_name}\n")    
                continue

            # 트랙별 참여 아티스트 조회 및 저장
            recording_id = track.get('recording', {}).get('id')
            recording_info = get(SharedInfo.get_musicbrainz_base_url() + f"recording/{recording_id}", params={
                'inc': 'artists',
                'fmt': 'json'
            })

            for artist_credit in recording_info.get('artist-credit', []):
                feat_artist_mbid = artist_credit['artist']['id']
                feat_artist_id = fetch_one(conn, "SELECT id FROM artist_tb WHERE mbid = %s", (feat_artist_mbid,))

                if not feat_artist_id:
                    feat_artist_id = store_artist.insertArtistTxn(mbid=feat_artist_mbid)["artist_id"]
                    logger.info(f"DB에 피처링 아티스트 {feat_artist_mbid} 추가됨.")
                else:
                    feat_artist_id = feat_artist_id[0]


                if feat_artist_mbid == mbid:
                    joinphrase = "main"  # 메인 아티스트 role = "main"

                joinphrase = normalize_joinphrase(artist_credit.get('joinphrase', ''))
                logger.info(f"피처링 joinphrase 정규화 전 {artist_credit.get('joinphrase', '').strip().lower()} /  정규화 후 {joinphrase}")
                # 피처링 가수 데이터 저장 (트랙-앨범 참여자 추가)
                insertArtistTrack(conn, feat_artist_id, track_id, joinphrase)

                # 중복 체크 후 앨범-아티스트 리스트에 추가
                if feat_artist_id not in feat_artists:
                    feat_artists[feat_artist_id] = joinphrase

        logger.info(f"앨범-아티스트 저장할 데이터 (feat_artists) : {feat_artists}")
        for feat_artist_id, joinphrase in feat_artists.items():
            insertArtistAlbum(conn, feat_artist_id, album_id, joinphrase)

    print(f"\n")


def insertTrack(conn, album_id, track_name, track_duration, track_rank):
    query = """
        INSERT INTO track_tb (album_id, track_name, duration, track_rank) 
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (album_id, track_name) DO NOTHING
        RETURNING id;
    """
    track_id = insert_data(conn, query, (album_id, track_name, track_duration, track_rank))
    if track_id:
        logger.info(f"(3-1) [DB] >> 트랙 데이터 삽입 완료 (track_id: {track_id} / track_name : {track_name})")
    return track_id[0] if track_id else None


def insertArtistTrack(conn, artist_id, track_id, joinphrase):
    query = """
        INSERT INTO artist_track_tb (artist_id, track_id, artist_role)
        VALUES (%s, %s, %s)
        ON CONFLICT DO NOTHING
    """
    execute_query(conn, query, (artist_id, track_id, joinphrase))
    logger.info(f"(3-2) [DB] >> 아티스트-트랙 관계 삽입 완료 (Artist ID: {artist_id}, Track ID: {track_id})")


def insertArtistAlbum(conn, artist_id, album_id, joinphrase):
    query = """
        INSERT INTO artist_album_tb (artist_id, album_id, artist_role)
        VALUES (%s, %s, %s)
        ON CONFLICT DO NOTHING
    """
    execute_query(conn, query, (artist_id, album_id, joinphrase))
    logger.info(f"(3-3) [DB] >> 아티스트-앨범 관계 삽입 완료 (Artist ID: {artist_id}, Album ID: {album_id})")
