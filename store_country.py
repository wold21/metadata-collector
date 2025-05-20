from utils.common_request import get
from shared_info import SharedInfo
import store_artist
import store_albums
from utils.logging_config import logger

def saveMusicData(country_name, genre=None, limit=50):
    """
    특정 국가의 전체 데이터를 MusicBrainz API에서 가져와 DB에 저장하는 함수
    :param country_name: 국가명 (예: 'Korea', 'Japan', 'United States')
    :param limit: 가져올 데이터 개수 (기본값 50)
    """
    if limit is None:
        limit = 100

    try:
        logger.info(f"[Country-Genre] ▶ {country_name} (✨장르:{genre if genre else '전체 장르'}) 데이터 조회 시작...")

        offset = 0
        total_cnt = 0  # 총 처리된 데이터 수
        while True:
            artists = fetch_artists_from_musicbrainz(country_name, genre, limit, offset)

            if not artists:
                logger.warning(f"[Country-Genre] {country_name} 데이터가 없습니다.")
                break

            # 아티스트 데이터를 처리하고 DB에 저장
            total_cnt = process_artist_data(country_name, genre, artists, total_cnt)

            # 만약 가져온 데이터가 limit보다 적으면 종료
            if len(artists) < limit:
                break

            # 다음 페이지로 이동
            offset += limit

        logger.info(f"[Country-Genre] {country_name} ✨{genre or '전체'} 데이터 저장 완료! (총 {total_cnt}명)")

    except Exception as e:
        logger.error(f"[Country-Genre] 오류 발생: {e}\n")


def fetch_artists_from_musicbrainz(country_name, genre=None, limit=50, offset=0):
    """
    MusicBrainz API에서 특정 국가와 장르에 해당하는 아티스트 데이터를 가져오는 함수
    :param country_name: 국가명 (예: 'Korea', 'Japan', 'United States')
    :param genre: 장르 (예: 'blues', 'electronic', 'kpop' 등, 선택사항)
    :return: 아티스트 데이터 목록
    """
    params = {
        'query': f'area:{country_name}',
        'fmt': 'json',
        'offset': offset,
        'limit': limit
    }

    if genre:
        params['query'] += f' AND tag:{genre}'  # 장르 추가

    try:
        response_json = get(SharedInfo.get_musicbrainz_base_url() + "artist/", params=params)
        return response_json.get('artists', [])
    except Exception as e:
        logger.error(f"[Country-Genre] MusicBrainz API 호출 중 오류 발생: {e}")
        return []

def process_artist_data(country_name, genre, artists, total_cnt):
    """
    아티스트 데이터를 처리하고, DB에 저장하는 함수
    :return: 업데이트된 처리된 데이터 수
    """
    for current_data_index, artist in enumerate(artists, start=total_cnt + 1):
        artist_name = artist.get('name')
        artist_mbid = artist.get('id')

        logger.info(f"[Country-Genre] {country_name} (✨장르:{genre if genre else '전체 장르'}) Artist {current_data_index}/{len(artists)} 번째 데이터 작업 시작 → {artist_name} ({artist_mbid})")

        # 아티스트 데이터를 DB에 저장
        artist_result = store_artist.insertArtistTxn(artist_name, artist_mbid)
        if artist_result:
            store_albums.insertArtistAlbumsTxn(artist_result['artist_mbid'])

    return total_cnt + len(artists)