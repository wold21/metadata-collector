from utils.database import get_connection, execute_query, fetch_one, fetch_one_dict, insert_data
from utils.logging_config import logger



def update_representative_covers(mbid):
    query = """

        WITH representative_cover AS (
            SELECT 
                TRIM(SPLIT_PART(at.title, '(', 1)) AS base_title,
                at.cover_path
            FROM album_tb at
            JOIN artist_album_tb aat ON at.id = aat.album_id
            JOIN artist_tb ar ON ar.id = aat.artist_id
            WHERE at.cover_path IS NOT NULL AND ar.mbid = %s
        ),
        target_albums AS (
            SELECT 
                at.id,
                TRIM(SPLIT_PART(at.title, '(', 1)) AS base_title
            FROM album_tb at
            JOIN artist_album_tb aat ON at.id = aat.album_id
            JOIN artist_tb ar ON ar.id = aat.artist_id
            WHERE at.cover_path IS NULL AND ar.mbid = %s
        )
        UPDATE album_tb target
        SET cover_path = rep.cover_path
        FROM representative_cover rep
        JOIN target_albums ta ON ta.base_title = rep.base_title
        WHERE target.id = ta.id;



    """

    with get_connection() as conn:
        updated_rows = execute_query(conn, query, (mbid, mbid))
        logger.info(f"[DB] >> 대표 이미지 없는 앨범들의 cover_path {updated_rows}건 업데이트 완료 (artist mbid: {mbid})")


update_representative_covers("ec2bcb77-b9a1-49e2-bfe7-419586bbef48")