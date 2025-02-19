from utils.common_request import get
import store_artist
import store_albums
from shared_info import SharedInfo
from utils.logging_config import logger


def getTopArtists():
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

    LIMIT = 100
    try:
        # for page in range(1, TOTAL_PAGE+1):
        response_json = get(SharedInfo.get_lastfm_base_url(), params = {
            'method': 'chart.gettopartists',
            'api_key': SharedInfo.get_api_key(),
            'format': 'json',
            'limit': 100,
            'page': 1
        })
        cnt = 0
        for artist in response_json['artists']['artist']:
            cnt += 1
            logger.info(f"\tTopArist 전체 {LIMIT} 중 {cnt} 번째 데이터 작업 시작")
            artist_result = store_artist.insertArtistTxn(artist['name'], artist['mbid'])
            album_result = store_albums.insertArtistAlbumsTxn(artist_result['artist_id'], artist_result['artist_name'], artist_result['artist_mbid'])
    except Exception as e:
        logger.error(f"오류 발생: {e}\n")

    
