import requests

def get(url, params):
    # 요청 URL 생성 및 출력
    full_url = f"{url}?" + "&".join([f"{key}={value}" for key, value in params.items()])
    print(f"✅ Request URL: {full_url}")

    response = requests.get(url, params=params)
    if(response.status_code == 200):
        return response.json()
    else:
        print(f"Error Code: {response.status_code}")
        return None