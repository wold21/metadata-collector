from utils.common_request import get
import store_artist
import store_albums
from shared_info import SharedInfo
from utils.logging_config import logger


def saveMusicData(limit=50):
    try:
        logger.info(f"[Top Artist] 데이터 조회 시작...")

        response_json = get(SharedInfo.get_lastfm_base_url(), params={
            'method': 'chart.gettopartists',
            'api_key': SharedInfo.get_lastfm_api_key(),
            'format': 'json',
            'limit': limit,
            'page': 1
        })

        artists = response_json['artists']['artist']
        success_names = []
        fail_names = []

        for idx, artist in enumerate(artists, start=1):
            artist_name = artist.get('name')
            artist_mbid = artist.get('mbid')

            logger.info(f"[Top Artist] {idx}/{len(artists)}번째 작업 시작 → {artist_name} ({artist_mbid})")

            try:
                artist_result = store_artist.insertArtistTxn(artist_name, artist_mbid)
                if artist_result:
                    success_names.append(artist_name)
                    store_albums.insertArtistAlbumsTxn(artist_result['artist_mbid'])
                else:
                    fail_names.append((artist_name, artist_mbid))
            except Exception as artist_e:
                fail_names.append((artist_name, artist_mbid))
                logger.error(f"[Artist] 저장 실패: '{artist_name}' 처리 중 오류 발생: {artist_e}")

        # 실패한 아티스트 재시도
        if fail_names:
            logger.info(f"🔁 실패한 {len(fail_names)}명의 아티스트 저장 재시도 시작...")
            retry_success, retry_fail = retry_failed_artists(fail_names)
            success_names.extend(retry_success)
            fail_names = retry_fail

        logger.info(f"[Top Artist] 성공: {len(success_names)} / 실패: {len(fail_names)} / 총: {len(artists)}명")
        logger.info(f"✅ 성공 아티스트: {', '.join(success_names) if success_names else '없음'}")
        logger.info(f"❌ 실패 아티스트: {', '.join(name for name, _ in fail_names) if fail_names else '없음'}")

    except Exception as e:
        logger.error(f"[Top Artist] 오류 발생: {e}")


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
