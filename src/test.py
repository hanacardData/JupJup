import requests
import os
from dotenv import load_dotenv

# 키 불러오기
load_dotenv()
client_id = os.getenv("NAVER_CLIENT_ID")
client_secret = os.getenv("NAVER_CLIENT_SECRET")

url = "https://openapi.naver.com/v1/search/blog.json"
headers = {
    "X-Naver-Client-Id": client_id,
    "X-Naver-Client-Secret": client_secret
}

params = {
    "query": "초콜릿",  
    "display": 1
}

response = requests.get(url, headers=headers, params=params)

print("응답 코드:", response.status_code)
if response.status_code == 200:
    print("API 연결 성공!")
    print("응답 데이터:", response.json())
else:
    print("연결 실패. 에러 메시지:")
    print(response.text)
