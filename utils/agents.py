from agno.agent import Agent
from agno.models.google import Gemini
from agno.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.googlesearch import GoogleSearchTools
from agno.tools.yfinance import YFinanceTools

from config import (
    DEFAULT_SESSION_ID,
    DEFAULT_USER_ID,
    GEMINI_API_KEY,
    GEMINI_MODEL_NAME,
    db,
)
from tools.technical_indicators import (
    get_bollinger_bands_signal,
    get_macd_signal,
    get_rsi_signal,
    get_sma_crossover_signal,
    get_vix_market_fear_signal,
)
from utils.prompt import SYSTEM_PROMPT


def create_finance_agent() -> Agent:
    return Agent(
        model=Gemini(
            id=GEMINI_MODEL_NAME,
            api_key=GEMINI_API_KEY,
            seed=42,
            system_prompt=SYSTEM_PROMPT,
        ),
        tools=[
            YFinanceTools(
                cache_results=True, exclude_tools=['get_historical_stock_prices']
            ),
            get_sma_crossover_signal,
            get_rsi_signal,
            get_macd_signal,
            get_bollinger_bands_signal,
            get_vix_market_fear_signal,
        ],
        name='Finance_Agent',
        id='agent_1',
        enable_agentic_memory=True,
        enable_user_memories=True,
        user_id=DEFAULT_USER_ID,
        session_id=DEFAULT_SESSION_ID,
        db=db,
    )


def create_sentiment_agent() -> Agent:
    return Agent(
        name='Sentiment_Agent',
        id='agent_2',
        model=Gemini(
            id=GEMINI_API_KEY, api_key=GEMINI_API_KEY, system_prompt=SYSTEM_PROMPT
        ),
        tools=[
            DuckDuckGoTools(cache_results=True),
            GoogleSearchTools(cache_results=True),
        ],
        user_id=DEFAULT_USER_ID,
        session_id=DEFAULT_SESSION_ID,
        enable_agentic_memory=True,
        enable_user_memories=True,
        db=db,
    )


def create_team() -> Team:
    finance_agent = create_finance_agent()
    sentiment_agent = create_sentiment_agent()

    return Team(
        id='team_1',
        name='PersonaQuantTeam',
        model=Gemini(
            id=GEMINI_MODEL_NAME, api_key=GEMINI_API_KEY, system_prompt=SYSTEM_PROMPT
        ),
        members=[finance_agent, sentiment_agent],
        db=db,
        user_id=DEFAULT_USER_ID,
        session_id=DEFAULT_SESSION_ID,
        add_history_to_context=True,
        num_history_runs=5,
        enable_session_summaries=True,
        enable_agentic_memory=True,
        enable_user_memories=True,
        add_session_summary_to_context=True,
        add_memories_to_context=True,
    )


team = create_team()
