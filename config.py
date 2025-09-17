import os

from agno.db.sqlite import SqliteDb
from dotenv import load_dotenv

_ = load_dotenv()

GEMINI_API_KEY: str | None = os.getenv('GOOGLE_API_KEY')
GEMINI_MODEL_NAME = 'gemini-2.5-flash-lite'
APP_HOST: str = '127.0.0.1'
APP_PORT: int = 8000

DB_FILE: str = 'agno.db'

DEFAULT_USER_ID: str = 'user_1234'
DEFAULT_SESSION_ID: str = 'session_user_1234'


db = SqliteDb(db_file=DB_FILE)
