# JupJup
네이버 웍스 줍줍이 레포

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
bot_secret = "****"
```

3. 의존성 설치
```bash
uv sync
```

4. 실행 (Batch)
```bash
schtasks /create /sc daily /st 09:00 /tn "JupJupTask" /tr "C:\your\path\run_batch.bat"
schtasks /query /tn "JupJupTask" /v /fo LIST # 확인
schtasks /delete /tn "JupJupTask" # 삭제
schtasks /run /tn "JupJupTask" # 테스트 실행
```

5. 실행 (Callback)
```bash
ngrok http 5000 # 설치 필요
python callback.py 2>&1 | Tee-Object -FilePath server.log
```
