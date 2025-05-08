import base64
import hashlib
import hmac

from secret import BOT_SECRET


def verify_signature(body: str, received_signature: str) -> bool:
    """요청 본문과 헤더의 X-WORKS-Signature를 비교"""
    hash_digest = hmac.new(
        BOT_SECRET.encode("utf-8"), body.encode("utf-8"), hashlib.sha256
    ).digest()
    signature = base64.b64encode(hash_digest).decode("utf-8")
    return hmac.compare_digest(signature, received_signature)
