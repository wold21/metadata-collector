import requests
from utils.logging_config import logger
from shared_info import SharedInfo


def get(url, params):
    # 요청 Full URL 생성 및 출력
    full_url = f"{url}?" + "&".join([f"{key}={value}" for key, value in params.items()])
    logger.info(f"✅ {full_url}")

    headers = {"User-Agent": SharedInfo.get_user_agent()} 
    response = requests.get(url, params=params, headers=headers) 

    if(response.status_code == 200):
        return response.json()
    else:
        logger.error(f"Error Code: {response.status_code}, Response: {response.text}")
        return None