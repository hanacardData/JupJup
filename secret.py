import os

from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.environ["client_id"]
CLIENT_SECRET = os.environ["client_secret"]
OPENAI_API_KEY = os.environ["openai_api_key"]
WORKS_CLIENT_ID = os.environ["works_client_id"]
WORKS_CLIENT_SECRET = os.environ["works_client_secret"]
SERVICE_ACCOUNT = os.environ["service_account"]
PRIVATE_KEY_PATH = os.environ["private_key_path"]
BOT_SECRET = os.environ["bot_secret"]
OPENWEATHER_API_KEY = os.environ["openweather_api_key"]
