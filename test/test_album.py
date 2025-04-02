# 아티스트에 대한 앨범/트랙 적제 테스트 파일 (store_album)
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from shared_info import SharedInfo  
from utils.logging_config import setup_logging, logger  # logger 객체도 직접 가져오기
import store_albums
# APIKEY = "a2540255f09a4e673d2adea41e633d10"

def start():
    SharedInfo.set_api_key("a2540255f09a4e673d2adea41e633d10")
    SharedInfo.set_lastfm_base_url('https://ws.audioscrobbler.com/2.0/')
    SharedInfo.set_musicbrainz_base_url('https://musicbrainz.org/ws/2/')
    
    logger.info("테스트 코드 시작")  # 로그 확인용 메시지

    # mbid
    store_albums.insertArtistAlbumsTxn('b6b21b0c-a706-4b46-a929-bd4d21b06cad')

start()