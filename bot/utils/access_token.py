import time

import jwt
import requests
from cryptography.hazmat.primitives import serialization

from logger import logger
from secret import (
    PRIVATE_KEY_PATH,
    SERVICE_ACCOUNT,
    WORKS_CLIENT_ID,
    WORKS_CLIENT_SECRET,
)


class TokenManager:
    def __init__(self):
        self._access_token = None
        self._token_expiry = 0  # unix timestamp

    def get_token(self) -> str:
        now = int(time.time())
        if self._access_token and now < self._token_expiry - 60:
            return self._access_token

        exp = now + 3600
        payload = {
            "iss": WORKS_CLIENT_ID,
            "sub": SERVICE_ACCOUNT,
            "iat": now,
            "exp": exp,
        }
        private_key = serialization.load_pem_private_key(
            PRIVATE_KEY_PATH.encode(), password=None
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
            self._access_token = token_data["access_token"]
            self._token_expiry = exp
            logger.info(f"Access Token: {self._access_token}")
            return self._access_token
        else:
            logger.error(f"Failed to get token: {response.status_code}")
            logger.error(response.text)
            raise Exception("Token request failed")


token_manager = TokenManager()


def set_headers() -> dict[str, str]:
    token = token_manager.get_token()
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
