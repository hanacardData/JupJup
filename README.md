# ScrapCompetitor
네이버 검색 API 스크랩하는 코드

## 사용법
1. `private.key`를 Naver works에서 발급, root 폴더에 저장한다.
2.`.env` 파일을 root에 생성 후 네이버, OpenAI의 service key를 아래와 같이 넣는다.
```python
# .env
## NAVER SCRAP API
client_id = "****"
client_secret = "****"

## OPENAI API
openai_api_key = "****"

## WORKS API
works_client_id = "****"
works_client_secret = "****"
service_account = "****"
private_key_path = "****" # 1번의 경로를 붙여넣는다
```

3. 의존성 설치
```bash
pip install -r requirements.txt
```
