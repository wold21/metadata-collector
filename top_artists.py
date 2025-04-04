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
        logger.info(f"▶ top artist 데이터 조회 시작...")
        response_json = get(SharedInfo.get_lastfm_base_url(), params = {
            'method': 'chart.gettopartists',
            'api_key': SharedInfo.get_lastfm_api_key(),
            'format': 'json',
            'limit': limit,
            'page': 1
        })

        artists = response_json['artists']['artist']

        cnt = 0
        for artist in artists:
            cnt += 1
            artist_name = artist.get('name')
            artist_mbid = artist.get('mbid')

            logger.info(f"\tTop Arist {cnt}/{len(artists)} 번째 데이터 작업 시작 → {artist_name} ({artist_mbid})")
            artist_result = store_artist.insertArtistTxn(artist_name, artist_mbid)
            if artist_result:
                store_albums.insertArtistAlbumsTxn(artist_result['artist_mbid'])

        logger.info(f"✔ Top artist 전체 데이터 저장 완료! (총 {len(artist)}명)")
    except Exception as e:
        logger.error(f"오류 발생: {e}\n")

    