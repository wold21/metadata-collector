import requests
from utils.logging_config import logger


def get(url, params):
    # 요청 Full URL 생성 및 출력
    full_url = f"{url}?" + "&".join([f"{key}={value}" for key, value in params.items()])
    logger.info(f"✅ Request URL: {full_url}")

    response = requests.get(url, params=params)
    if(response.status_code == 200):
        return response.json()
    else:
        logger.error(f"Error Code: {response.status_code}, Response: {response.text}")
        return None