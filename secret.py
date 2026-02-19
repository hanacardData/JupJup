import os

from dotenv import load_dotenv

if os.path.exists(".env"):
    load_dotenv()


CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
WORKS_CLIENT_ID = os.environ["WORKS_CLIENT_ID"]
WORKS_CLIENT_SECRET = os.environ["WORKS_CLIENT_SECRET"]
SERVICE_ACCOUNT = os.environ["SERVICE_ACCOUNT"]

_PRIVATE_KEY_PATH = os.environ["PRIVATE_KEY_PATH"]
if _PRIVATE_KEY_PATH.endswith(".key"):
    with open(_PRIVATE_KEY_PATH, "r") as key_file:
        PRIVATE_KEY_PATH = key_file.read()
else:
    PRIVATE_KEY_PATH = _PRIVATE_KEY_PATH

BOT_SECRET = os.environ["BOT_SECRET"]
