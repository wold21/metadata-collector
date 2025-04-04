# 아티스트 추가 테스트 파일 (store_artist)
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from shared_info import SharedInfo  
from utils.logging_config import setup_logging, logger  # logger 객체도 직접 가져오기
import store_artist

def start():
    SharedInfo.set_lastfm_api_key("a2540255f09a4e673d2adea41e633d10")
    SharedInfo.set_lastfm_base_url('https://ws.audioscrobbler.com/2.0/')
    SharedInfo.set_musicbrainz_base_url('https://musicbrainz.org/ws/2/')
    SharedInfo.set_theaudiodb_base_url('https://www.theaudiodb.com/api/v1/json/')
    SharedInfo.set_theaudiodb_api_key('523532')
    
    logger.info("테스트 코드 시작")  # 로그 확인용 메시지
    store_artist.insertArtistTxn("10CM")

start()