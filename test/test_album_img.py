import sys
import os
import json
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from shared_info import SharedInfo  
from utils.logging_config import logger  
from utils.common_request import get 

logger = logging.getLogger(__name__)

def get_album_images(mb_release_group_id):
    """TheAudioDB API를 사용하여 앨범 이미지 가져오기"""
    try:
        response = get(SharedInfo.get_theaudiodb_base_url() + SharedInfo.get_theaudiodb_api_key() + f"/album-mb.php",
            params={"i": mb_release_group_id}
        )
        if not response:  
            logger.warning(f"[TheAudioDB] 응답 없음: {mb_release_group_id}")
            return None

        logger.info(f"[TheAudioDB] 응답 데이터: {json.dumps(response, indent=2, ensure_ascii=False)}")

        if "album" in response and response["album"]:
            album_image = response["album"][0].get("strAlbumThumb")
            if album_image:
                return album_image
        
        return None

    except Exception as e:
        logger.error(f"[TheAudioDB] 요청 오류: {e}")
        return None

def fetch_all_albums(mbid):
    """MusicBrainz API에서 limit=100으로 나눠서 모든 앨범 가져오기"""
    base_url = SharedInfo.get_musicbrainz_base_url() + "release-group/"
    albums = []
    offset = 0
    limit = 100  # 100개 넘어가면 limit 100으로 고정됨

    first_response = get(base_url, params={'artist': mbid, 'fmt': 'json'})
    total_albums = first_response.get('release-group-count', 0)
    logger.info(f"총 {total_albums}개의 앨범 발견")

    while offset < total_albums:
        response = get(base_url, params={
            'artist': mbid,
            'inc': 'genres',
            'limit': limit,
            'offset': offset,
            'fmt': 'json',
        })
        
        if "release-groups" in response:
            albums.extend(response["release-groups"])

        offset += limit 

    return albums


def start():
    SharedInfo.set_lastfm_api_key("a2540255f09a4e673d2adea41e633d10")
    SharedInfo.set_lastfm_base_url('https://ws.audioscrobbler.com/2.0/')
    SharedInfo.set_musicbrainz_base_url('https://musicbrainz.org/ws/2/')
    SharedInfo.set_theaudiodb_base_url('https://www.theaudiodb.com/api/v1/json/')
    SharedInfo.set_theaudiodb_api_key('523532')
    
    logger.info("테스트 코드 시작")

    # mbid = "c8b03190-306c-4120-bb0b-6f2ebfc06ea9" #The Weeknd   총 196개 앨범 중 33개의 앨범 이미지 찾음!
    # mbid = "cc197bad-dc9c-440d-a5b5-d52ba2e14234" #Coldplay    총 262개 앨범 중 51개의 앨범 이미지 찾음!
    mbid = "20244d07-534f-4eff-b4d4-930878889970" #Taylor Swift 총 377개 앨범 중 29개의 앨범 이미지 찾음!

    
    albums_info = fetch_all_albums(mbid)  # 앨범의 releases 데이터 조회

    total_albums = len(albums_info)
    albums_with_images = 0

    for album in albums_info:
        mb_release_group_id = album.get("id")
        if mb_release_group_id:
            album_image = get_album_images(mb_release_group_id)

            if album_image:
                albums_with_images += 1
                logger.info(f"🎵 앨범: {album.get('title')} | 📸 이미지 URL: {album_image} | mb_release_group_id: {mb_release_group_id}")
            else:
                logger.warning(f"🎵 앨범: {album.get('title')} | 🚫 앨범 이미지 없음 | mb_release_group_id: {mb_release_group_id}")

    logger.info(f"✅ 총 {total_albums}개 앨범 중 {albums_with_images}개의 앨범 이미지 찾음!")

start()
