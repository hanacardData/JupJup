# ScrapCompetitor
네이버 검색 API 스크랩하는 코드

## 사용법
1. **`fetch.py` 예처럼 원하는 input으로 데이터를 가져올 수 있다.**
2. `.env` 파일을 root에 생성 후 네이버, OpenAI의 service key를 아래와 같이 넣는다.
```python
# .env
client_id = "****"
client_secret = "****"
openai_api_key = "****"
```

참고) 파일 생성 후 폴더 구조
```bash
ScrapCompetitor
│  .env # 반드시 필요!
│  .gitignore
│  .env
│  .gitignore
│  .pre-commit-config.yaml
│  choose.py
│  fetch.py
│  load.py
│  logger.py
│  README.md
│  refine.py
│  requirements.txt
│  secret.py
│  variables.py
└─models
   │  request.py
   │  response.py
   └─__init__.py
```

3. 의존성 설치 및 실행
```bash
pip install -r requirements.txt
python fetch.py # Working on
```

4. 참고
blog: https://developers.naver.com/docs/serviceapi/search/blog/blog.md#%ED%8C%8C%EB%9D%BC%EB%AF%B8%ED%84%B0
news: https://developers.naver.com/docs/serviceapi/search/news/news.md#%ED%8C%8C%EB%9D%BC%EB%AF%B8%ED%84%B0
cafe: https://developers.naver.com/docs/serviceapi/search/cafearticle/cafearticle.md#%ED%8C%8C%EB%9D%BC%EB%AF%B8%ED%84%B0
datalab: https://developers.naver.com/docs/serviceapi/datalab/search/search.md#%ED%8C%8C%EB%9D%BC%EB%AF%B8%ED%84%B0.
