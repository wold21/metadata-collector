import logging

# 로그 설정 함
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,  # 로그 레벨 설정
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("log.txt"),  # 파일로 로그 저장
            logging.StreamHandler()  # 콘솔에도 출력
        ]
    )

setup_logging()

# 로깅 객체 가져오기
logger = logging.getLogger()