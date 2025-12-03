import os

from dotenv import load_dotenv

if os.path.exists(".env"):
    load_dotenv()


CLIENT_ID = os.environ["client_id"]
CLIENT_SECRET = os.environ["client_secret"]
OPENAI_API_KEY = os.environ.get("openai_api_key")
WORKS_CLIENT_ID = os.environ["works_client_id"]
WORKS_CLIENT_SECRET = os.environ["works_client_secret"]
SERVICE_ACCOUNT = os.environ["service_account"]

_PRIVATE_KEY_PATH = os.environ["private_key_path"]
if _PRIVATE_KEY_PATH.endswith(".key"):
    with open(_PRIVATE_KEY_PATH, "r") as key_file:
        PRIVATE_KEY_PATH = key_file.read()
else:
    PRIVATE_KEY_PATH = _PRIVATE_KEY_PATH

BOT_SECRET = os.environ["bot_secret"]
