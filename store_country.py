from utils.common_request import get
from shared_info import SharedInfo
import store_artist
import store_albums
from utils.logging_config import logger

def saveMusicData(country_name, genre=None, limit=50):
    if limit is None:
        limit = 100

    logger.info(f"[Country-Genre] ▶ {country_name} (✨장르:{genre or '전체 장르'}) 데이터 조회 시작...")

    offset = 0
    record_index = 1
    success_names = []
    fail_names = []
    total_records = None

    while True:
        artists, total_records = fetch_artists_from_musicbrainz(country_name, genre, limit, offset)
        if not artists:
            logger.warning(f"[Country-Genre] {country_name} 데이터가 없습니다.")
            break

        for i, artist in enumerate(artists, start=1):
            artist_name = artist.get('name')
            artist_mbid = artist.get('id')

            logger.info(
                f"[Country-Genre] {country_name} (✨장르:{genre or '전체 장르'}) "
                f"Artist {record_index}/{total_records or '?'}번째 작업 시작 → {artist_name} ({artist_mbid})"
            )

            try:
                result = store_artist.insertArtistTxn(artist_name, artist_mbid)
                if result:
                    store_albums.insertArtistAlbumsTxn(result['artist_mbid'])
                    success_names.append(artist_name)
                else:
                    fail_names.append((artist_name, artist_mbid))
            except Exception as e:
                fail_names.append((artist_name, artist_mbid))
                logger.error(f"[Country-Genre] 저장 실패: '{artist_name}' 처리 중 오류 발생: {e}")

            record_index += 1

        offset += limit
        if offset >= (total_records or 0):
            break

    # 재시도
    if fail_names:
        logger.info(f"🔁 실패한 {len(fail_names)}명의 아티스트 저장 재시도 시작...")
        retry_success, retry_fail = retry_failed_artists(fail_names)
        success_names.extend(retry_success)
        fail_names = retry_fail  # 재시도 이후에도 실패한 아티스트만 남김

    logger.info(f"[Country-Genre] {country_name} ✨{genre or '전체'} - 성공: {len(success_names)} / 실패: {len(fail_names)} / 총 처리: {record_index - 1}명")
    logger.info(f"✅ 성공 아티스트: {', '.join(success_names) if success_names else '없음'}")
    logger.info(f"❌ 실패 아티스트: {', '.join(name for name, _ in fail_names) if fail_names else '없음'}")

def fetch_artists_from_musicbrainz(country_name, genre=None, limit=50, offset=0):
    params = {
        'query': f'area:{country_name}',
        'fmt': 'json',
        'offset': offset,
        'limit': limit
    }

    if genre:
        params['query'] += f' AND tag:{genre}'

    try:
        response_json = get(SharedInfo.get_musicbrainz_base_url() + "artist/", params=params)
        artists = response_json.get('artists', [])
        count = response_json.get('count', 0)
        return artists, count
    except Exception as e:
        logger.error(f"[Country-Genre] MusicBrainz API 호출 중 오류 발생: {e}")
        return [], 0

def retry_failed_artists(fail_list):
    success = []
    still_fail = []

    for artist_name, artist_mbid in fail_list:
        try:
            logger.info(f"[Retry] 저장 재시도 중 → {artist_name} ({artist_mbid})")
            result = store_artist.insertArtistTxn(artist_name, artist_mbid)
            if result:
                store_albums.insertArtistAlbumsTxn(result['artist_mbid'])
                success.append(artist_name)
            else:
                still_fail.append((artist_name, artist_mbid))
        except Exception as e:
            still_fail.append((artist_name, artist_mbid))
            logger.error(f"[Retry] 저장 실패: '{artist_name}' 재시도 중 오류 발생: {e}")

    return success, still_fail

