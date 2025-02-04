import requests

def get(url, params):
    response = requests.get(url, params=params)
    if(response.status_code == 200):
        return response.json()
    else:
        print(f"Error Code: {response.status_code}")
        return None