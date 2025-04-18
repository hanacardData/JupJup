import time

import jwt
import requests
from cryptography.hazmat.primitives import serialization

from secret import (
    PRIVATE_KEY_PATH,
    SERVICE_ACCOUNT,
    WORKS_CLIENT_ID,
    WORKS_CLIENT_SECRET,
)


def get_token() -> str:
    """Works API에 접근하기 위한 JWT 토큰을 생성해서 인증하기 위한 Access token 받아오는 함수."""
    iat = int(time.time())
    exp = iat + 3600  # 1시간 후 만료
    payload = {
        "iss": WORKS_CLIENT_ID,
        "sub": SERVICE_ACCOUNT,
        "iat": iat,
        "exp": exp,
    }

    with open(PRIVATE_KEY_PATH, "r") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read().encode(), password=None
        )

    encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")

    token_url = "https://auth.worksmobile.com/oauth2/v2.0/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
    data = {
        "assertion": encoded_jwt,
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "client_id": WORKS_CLIENT_ID,
        "client_secret": WORKS_CLIENT_SECRET,
        "scope": "bot bot.message bot.read",
    }

    response = requests.post(token_url, headers=headers, data=data)
    if response.status_code == 200:
        token_data: dict[str, str] = response.json()
        print("✅ Access Token:", token_data["access_token"])
        return token_data["access_token"]
    else:
        print("❌ Failed to get token:", response.status_code)
        print(response.text)
