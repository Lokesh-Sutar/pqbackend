import os

from agno.db.sqlite import SqliteDb
from dotenv import load_dotenv

_ = load_dotenv()

GOOGLE_API_KEY_0: str | None = os.getenv('GOOGLE_API_KEY_0')
GOOGLE_API_KEY_1: str | None = os.getenv('GOOGLE_API_KEY_1')
GOOGLE_API_KEY_2: str | None = os.getenv('GOOGLE_API_KEY_2')
GOOGLE_API_KEY_3: str | None = os.getenv('GOOGLE_API_KEY_3')

GOOGLE_MODEL_NAME_0 = 'gemini-2.5-pro'
GOOGLE_MODEL_NAME_1 = 'gemini-2.5-flash'

OPENROUTER_MODEL_NORMAL = 'gpt-oss-120b:free'
OPENROUTER_MODEL_REASONING = 'moonshotai/kimi-k2:free'
OPENROUTER_MODEL_REASONING_PROVIDER = 'moonshotai'
OPENROUTER_MODEL_API: str | None = os.getenv('OPENROUTER_MODEL_API')

APP_HOST: str = '127.0.0.1'
APP_PORT: int = 8000

DB_FILE: str = 'agno.db'

DEFAULT_USER_ID: str = 'user_1234'
DEFAULT_SESSION_ID: str = 'session_user_1234'

DEBUG_MODE = False
DEBUG_LEVEL = 2  # 1 or 2

db = SqliteDb(db_file=DB_FILE)
