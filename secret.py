import os

from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.environ["client_id"]
CLIENT_SECRET = os.environ["client_secret"]
OPENAI_API_KEY = os.environ["openai_api_key"]
