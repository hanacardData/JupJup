import requests
import os
from dotenv import load_dotenv
from pathlib import Path

# .env 경로 명확히 설정 (src/.env 기준)
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# 키 불러오기
client_id = os.getenv("NAVER_CLIENT_ID")
client_secret = os.getenv("NAVER_CLIENT_SECRET")

# 요청 URL
url = "https://openapi.naver.com/v1/datalab/search"

# 요청 헤더
headers = {
    "X-Naver-Client-Id": client_id,
    "X-Naver-Client-Secret": client_secret,
    "Content-Type": "application/json"
}

# 요청 바디 (검색 트렌드 조건)
data = {
    "startDate": "2024-12-01",
    "endDate": "2024-12-31",
    "timeUnit": "date",
    "keywordGroups": [
        {
            "groupName": "하나카드",
            "keywords": ["원더카드", "제이드카드", "트래블로그"]
        }
    ]
}

# POST 요청
response = requests.post(url, headers=headers, json=data)

# 결과 출력
print("응답 코드:", response.status_code)
if response.status_code == 200:
    print("데이터랩 응답 성공!")
    print("응답 데이터:", response.json())
else:
    print("실패. 응답 메시지:")
    print(response.text)
