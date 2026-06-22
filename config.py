import os

from agno.db.sqlite import SqliteDb
from dotenv import load_dotenv

_ = load_dotenv()

GOOGLE_API_KEY_0: str | None = os.getenv('GOOGLE_API_KEY_0')
GOOGLE_API_KEY_1: str | None = os.getenv('GOOGLE_API_KEY_1')
GOOGLE_API_KEY_2: str | None = os.getenv('GOOGLE_API_KEY_2')
GOOGLE_API_KEY_3: str | None = os.getenv('GOOGLE_API_KEY_3')
GOOGLE_API_KEY_4: str | None = os.getenv('GOOGLE_API_KEY_4')
GROQ_API_KEY: str | None = os.getenv('GROQ_API_KEY')
OPENROUTER_MODEL_API: str | None = os.getenv('OPENROUTER_MODEL_API')
REDDIT_CLIENT_ID: str | None = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET: str | None = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT: str | None = os.getenv('REDDIT_USER_AGENT')
FINNHUB_API_KEY: str | None = os.getenv('FINNHUB_API_KEY')
LINKUP_API_KEY: str | None = os.getenv('LINKUP_API_KEY')
HF_API_KEY: str | None = os.getenv('HF_API_KEY')
CEREBRAS_API_KEY: str | None = os.getenv('CEREBRAS_API_KEY')

GOOGLE_MODEL_PRO = 'gemini-2.5-pro'
# GOOGLE_MODEL_FLASH = 'gemini-2.5-flash'
GOOGLE_MODEL_FLASH = 'gemma-4-31b-it'
GOOGLE_MODEL_FLASH_EXP = 'gemini-flash-latest'
GOOGLE_MODEL_FLASH_LITE = 'gemini-flash-lite-latest'

OPENROUTER_MODEL_NORMAL = 'openai/gpt-oss-120b:free'
OPENROUTER_MODEL_REASONING = 'moonshotai/kimi-k2:free'
OPENROUTER_MODEL_REASONING_PROVIDER = 'moonshotai'

APP_HOST: str = '127.0.0.1'
APP_PORT: int = 8000

DB_FILE: str = 'agno.db'

DEFAULT_USER_ID: str = 'user_1234'
DEFAULT_SESSION_ID: str = 'session_user_1234'
FINANCE_AGENT_ID = 'agent_1'
SENTIMENT_AGENT_ID = 'agent_2'
ADVISORY_AGENT_ID = 'agent_3'
SEARCH_AGENT_ID = 'agent_4'

TEAM_NAME_ID = 'team_1'

DEBUG_MODE = False
DEBUG_LEVEL = 1

REASONING_MODE = False

COMMON_RETRY_SETTINGS = {
    'exponential_backoff': True,
    'retries': 5,
    'delay_between_retries': 3,
}
db = SqliteDb(db_file=DB_FILE)

COMMON_AGENT_USER_SETTINGS = {
    'markdown': True,
    'user_id': DEFAULT_USER_ID,
    'session_id': DEFAULT_SESSION_ID,
    'debug_mode': DEBUG_MODE,
    'debug_level': DEBUG_LEVEL,
    # 'reasoning': REASONING_MODE,
    # 'reasoning_max_steps': 2,
    # 'db': db,
}

TEAM_USER_SETTINGS = {
    'markdown': True,
    'user_id': DEFAULT_USER_ID,
    'session_id': DEFAULT_SESSION_ID,
    'debug_mode': DEBUG_MODE,
    'debug_level': DEBUG_LEVEL,
    # 'db': db,
}
