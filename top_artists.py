from utils.common_request import get
import store_artist
import store_albums
from shared_info import SharedInfo
from utils.logging_config import logger

# TOP 100 artist 데이터 수집
def saveMusicData(limit=50):
    
    # LIMIT = 1
    # TOTAL_PAGE = None
    # response_json = get(SharedInfo.get_lastfm_base_url(), params = {
    #     'method': 'chart.gettopartists',
    #     'api_key': SharedInfo.get_api_key(),
    #     'format': 'json',
    #     'limit': LIMIT,
    #     'page': 1
    # })
    
    # TOTAL_PAGE = int(response_json['artists']['@attr']['totalPages'])
    # logger.info(f"(0) 전체 TopArist 수 : {TOTAL_PAGE}")
    # for page in range(65, TOTAL_PAGE+1):

    try:
        logger.info(f"[Top Arist] 데이터 조회 시작...")
        response_json = get(SharedInfo.get_lastfm_base_url(), params = {
            'method': 'chart.gettopartists',
            'api_key': SharedInfo.get_lastfm_api_key(),
            'format': 'json',
            'limit': limit,
            'page': 1
        })

        artists = response_json['artists']['artist']

        success_names = []
        fail_names = []

        cnt = 0
        for idx, artist in enumerate(artists, start=1):
            cnt += 1
            artist_name = artist.get('name')
            artist_mbid = artist.get('mbid')

            logger.info(f"[Top Artist] {idx}/{len(artists)}번째 작업 시작 → {artist_name} ({artist_mbid})")

            try:
                artist_result = store_artist.insertArtistTxn(artist_name, artist_mbid)
                if artist_result:
                    success_names.append(artist_name)
                    store_albums.insertArtistAlbumsTxn(artist_result['artist_mbid'])
                else:
                    fail_names.append(artist_name)
            except Exception as artist_e:
                fail_names.append(artist_name)
                logger.error(f"[Artist] 저장 실패: '{artist_name}' 처리 중 오류 발생: {artist_e}")

        logger.info(f"[Top Artist] 성공: {len(success_names)} / 실패: {len(fail_names)} / 총: {len(artists)}명")
        logger.info(f"✅ 성공 아티스트: {', '.join(success_names) if success_names else '없음'}")
        logger.info(f"❌ 실패 아티스트: {', '.join(fail_names) if fail_names else '없음'}")

    except Exception as e:
        logger.error(f"[Top Arist] 오류 발생: {e}\n")

    