from utils.common_request import get
from shared_info import SharedInfo
import store_artist
import store_albums
from utils.logging_config import logger

def saveMusicData(country_name, limit=50):
    """
    특정 국가의 전체 데이터를 MusicBrainz API에서 가져와 DB에 저장하는 함수
    :param country_name: 국가명 (예: 'Korea', 'Japan', 'United States')
    :param limit: 가져올 데이터 개수 (기본값 50)
    """

    try:
        logger.info(f"▶ {country_name} 데이터 조회 시작...")
        response_json = get(SharedInfo.get_musicbrainz_base_url() + "artist/", params={
            'query': f'area:{country_name}',
            'fmt': 'json',
            'limit': limit
        })

        artists = response_json.get('artists', [])
        if not artists:
            logger.warning(f"{country_name} 데이터가 없습니다.")
            return

        cnt = 0
        for artist in artists:
            cnt += 1
            artist_name = artist.get('name')
            artist_mbid = artist.get('id')

            logger.info(f"\t{country_name} Artist {cnt}/{len(artists)} 번째 데이터 작업 시작 → {artist_name} ({artist_mbid})")

            artist_result = store_artist.insertArtistTxn(artist_name, artist_mbid)

            if artist_result:
                store_albums.insertArtistAlbumsTxn(artist_result['artist_mbid'])

        logger.info(f"✔ {country_name} 전체 데이터 저장 완료! (총 {len(artists)}명)")

    except Exception as e:
        logger.error(f"오류 발생: {e}\n")