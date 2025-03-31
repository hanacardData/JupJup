# ScrapCompetitor
네이버 검색 API 스크랩하는 코드

## 사용법
1. **`fetch.py` 예처럼 원하는 input으로 데이터를 가져올 수 있다.**
2. `.env` 파일을 root에 생성 후 공공데이터포털의 service key를 아래와 같이 넣는다.
```python
# .env
client_id = "****"
client_secret = "****"
```

참고) 파일 생성 후 폴더 구조
```bash
scrapNPS
│  .env # 반드시 필요!
│  .gitignore
│  .pre-commit-config.yaml
│  fetch.py
│  logger.py
│  README.md
├─.github
└─models
```

3. 의존성 설치 및 실행
```bash
pip install -r requirements.txt
python fetch.py # Working on
```
