from utils.common_request import get
import store_artist
import store_albums
from utils.logging_config import logger


def saveMusicData(artist_names):
    try:
        logger.info(f"[이름으로 가수들 저장] 데이터 조회 시작...")

        success_names = []
        fail_names = []

        for idx, artist_name in enumerate(artist_names, start=1):
            try:
                logger.info(f"[이름으로 가수들 저장] {idx}/{len(artist_names)}번째 작업 시작 → {artist_name}")

                # 아티스트 정보 저장
                artist_result = store_artist.insertArtistTxn(artist_name)

                if artist_result:
                    success_names.append(artist_name)
                    # 앨범 정보 저장
                    store_albums.insertArtistAlbumsTxn(artist_result['artist_mbid'])
                else:
                    fail_names.append(artist_name)

            except Exception as artist_e:
                fail_names.append(artist_name)
                logger.error(f"[Artist] 저장 실패: '{artist_name}' 처리 중 오류 발생: {artist_e}")

        # 실패한 아티스트 재시도
        if fail_names:
            logger.info(f"🔁 실패한 {len(fail_names)}명의 아티스트 저장 재시도 시작...")
            retry_success, retry_fail = retry_failed_artists(fail_names)
            success_names.extend(retry_success)
            fail_names = retry_fail

        logger.info(f"[이름으로 가수들 저장] 성공: {len(success_names)} / 실패: {len(fail_names)} / 총: {len(artist_names)}명")
        logger.info(f"✅ 성공 아티스트: {', '.join(success_names) if success_names else '없음'}")
        logger.info(f"❌ 실패 아티스트: {', '.join(fail_names) if fail_names else '없음'}")

    except Exception as e:
        logger.error(f"[이름으로 가수들 저장] 오류 발생: {e}")


def retry_failed_artists(fail_list):
    success = []
    still_fail = []

    for artist_name in fail_list:
        try:
            logger.info(f"[Retry] 저장 재시도 중 → {artist_name}")
            result = store_artist.insertArtistTxn(artist_name)
            if result:
                store_albums.insertArtistAlbumsTxn(result['artist_mbid'])
                success.append(artist_name)
            else:
                still_fail.append(artist_name)
        except Exception as e:
            still_fail.append(artist_name)
            logger.error(f"[Retry] 저장 실패: '{artist_name}' 재시도 중 오류 발생: {e}")

    return success, still_fail
