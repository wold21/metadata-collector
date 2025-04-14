import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))  # 현재 디렉토리 추가

import argparse
from shared_info import SharedInfo
from utils.logging_config import setup_logging, logger
import top_artists
import store_country
import store_artist
import store_albums


def start(mode, artist_name=None, artist_mbid=None, country=None, genre=None, limit=None):
    """선택한 데이터 적재 실행"""
    logger.info(f"애플리케이션 실행 (mode: {mode}, name: {artist_name}, mbid: {artist_mbid}, country: {country}, genre: {genre}, limit: {limit})")

    if mode == "top_artists":
        top_artists.saveMusicData(limit)

    elif mode == "country":
        if not country:
            logger.error("국가명을 입력해야 합니다. 예: --mode country --country 'Korea'")
            return
        store_country.saveMusicData(country, genre, limit)

    elif mode == "artist":
        if artist_name or artist_mbid:
            store_artist.insertArtistTxn(artist_name, artist_mbid)
        else:
            logger.error("아티스트명 또는 MBID를 입력해야 합니다. 예: --mode artist --name 'BTS' 또는 --mbid '1ce70900-77b1-4d8d-8bb6-0fb1237c3d49'")
            return

        store_artist.insertArtistTxn(artist_name, artist_mbid)

    elif mode == "album":
        if not artist_mbid:
            logger.error("아티스트 MBID를 입력해야 합니다. 예: --mode album --mbid '1ce70900-77b1-4d8d-8bb6-0fb1237c3d49'")
            return
        store_albums.insertArtistAlbumsTxn(artist_mbid)

    else:
        logger.error("지원되지 않는 모드입니다. 선택 가능한 모드: top_artists, country, artist, album")
        return

    logger.info(f"✔ {mode} 데이터 적재 완료")

if __name__ == "__main__":
    # 공통 설정
    SharedInfo.set_lastfm_api_key("a2540255f09a4e673d2adea41e633d10")
    SharedInfo.set_lastfm_base_url("https://ws.audioscrobbler.com/2.0/")
    SharedInfo.set_musicbrainz_base_url("https://musicbrainz.org/ws/2/")
    SharedInfo.set_theaudiodb_base_url('https://www.theaudiodb.com/api/v1/json/')
    SharedInfo.set_theaudiodb_api_key('523532')

    # 실행 모드 설정
    parser = argparse.ArgumentParser(description="데이터 적재 실행")
    parser.add_argument("--mode", type=str, required=True, help="실행 모드 (top_artists / country / artist / album)")
    parser.add_argument("--name", type=str, help="아티스트명")
    parser.add_argument("--mbid", type=str, help="아티스트 MBID")
    parser.add_argument("--country", type=str, help="국가명(ISO 3166-1 country names standard)")
    parser.add_argument("--genre", type=str, choices=['blues', 'hip hop', 'electronic', 'jazz', 'lo-fi', 'rock', 'chill', 'acoustic', 'rnb', 'pop', 'ballad', 'indie', 'kpop'], help="장르")
    parser.add_argument("--limit", type=int, help="가져올 데이터 개수 (기본값: 50)")

    args = parser.parse_args()
    start(args.mode, args.name, args.mbid, args.country, args.genre, args.limit)