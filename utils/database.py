import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor
from utils.logging_config import logger


DB_CONFIG = {
    "dbname": "onhz",
    "user": "onhz",
    "password": "onhz",
    "host": "220.116.96.179",
    "port": "65432"
}

def get_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        logger.error(f"데이터베이스 연결 실패: {e}")
        return None


def execute_query(conn, query, params=None, fetch_one=False, fetch_all=False, commit=False):
    try:
        cur = conn.cursor()
        cur.execute(query, params or ())
        affected_rows = cur.rowcount 

        if fetch_one:
            result = cur.fetchone()
        elif fetch_all:
            result = cur.fetchall()
        else:
            result = affected_rows 
        
        if commit:
            conn.commit()

        return result
    except psycopg2.Error as e:
        logger.error(f" DB 오류: {e}")
        conn.rollback()
        return None


def insert_data(conn, query, params):
    """ INSERT 쿼리 실행 (중복 방지 ON CONFLICT 지원) """   
    # 만약 결과로 반환된 ID가 None이면, 쿼리 로그를 출력
    result = execute_query(conn, query, params, fetch_one=True, commit=True)
    if result is None:
        logger.warning(f"insert return ID 없음 : {query} / 파라미터: {params}")
    return result


def fetch_one(conn, query, params):
    """ SELECT 쿼리 실행 (단일 결과 조회) """
    return execute_query(conn, query, params, fetch_one=True)


def fetch_all(conn, query, params=None):
    """ SELECT 쿼리 실행 (여러 개 결과 조회) """
    return execute_query(conn, query, params, fetch_all=True)

def fetch_one_dict(conn, query, params):
    """ SELECT 쿼리 실행 (딕셔너리 형태로 반환) """
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(query, params if params else ())
            result = cur.fetchone()
            return dict(result) if result else None  # 딕셔너리 형태로 변환
    except psycopg2.Error as e:
        logger.error(f" DB 오류: {e}")
        return None
    