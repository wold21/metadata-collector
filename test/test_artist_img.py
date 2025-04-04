# mbid로 아티스트 이미지를 가져오는 테스트 코드
import sys
import os
import json
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from shared_info import SharedInfo  
from utils.logging_config import logger  
from utils.common_request import get 

logger = logging.getLogger(__name__)


def get_artist_image(mb_artist_id):
    """TheAudioDB API를 사용하여 아티스트 이미지 가져오기"""
    try:
        response = get(SharedInfo.get_theaudiodb_base_url() + SharedInfo.get_theaudiodb_api_key() + "/artist-mb.php",
            params={"i": mb_artist_id}
        )
        if not response:
            logger.warning(f"[TheAudioDB] 아티스트 응답 없음: {mb_artist_id}")
            return None

        logger.info(f"[TheAudioDB] 아티스트 응답 데이터: {json.dumps(response, indent=2, ensure_ascii=False)}")

        if "artists" in response and response["artists"]:
            artist_image = response["artists"][0].get("strArtistThumb")
            return artist_image
        
        return None

    except Exception as e:
        logger.error(f"[TheAudioDB] 아티스트 요청 오류: {e}")
        return None


def start():
    SharedInfo.set_theaudiodb_base_url('https://www.theaudiodb.com/api/v1/json/')
    SharedInfo.set_theaudiodb_api_key('523532')
    
    logger.info("테스트 코드 시작")

    # 예시: 유명 아티스트 mbid
    # mbid = "20244d07-534f-4eff-b4d4-930878889970"  # Taylor Swift
    # mbid = "c8b03190-306c-4120-bb0b-6f2ebfc06ea9"  # The Weeknd
    mbid = "cc197bad-dc9c-440d-a5b5-d52ba2e14234"    # Coldplay

    image_url = get_artist_image(mbid)

    if image_url:
        logger.info(f"🖼️ 아티스트 이미지 URL: {image_url}")
    else:
        logger.warning("🚫 아티스트 이미지 없음")

start()
