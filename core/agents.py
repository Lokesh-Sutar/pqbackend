from agno.agent import Agent
from agno.models.google import Gemini
from agno.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.googlesearch import GoogleSearchTools
from agno.tools.yfinance import YFinanceTools

from config import (
    DEBUG_LEVEL,
    DEBUG_MODE,
    DEFAULT_SESSION_ID,
    DEFAULT_USER_ID,
    GOOGLE_API_KEY_0,
    GOOGLE_API_KEY_1,
    GOOGLE_API_KEY_2,
    GOOGLE_MODEL_NAME_0,
    GOOGLE_MODEL_NAME_1,
    REASONING_MODE,
    db,
)
from tools.sentiment.finhub import get_finnhub_news_sentiment
from tools.sentiment.reddit import get_reddit_sentiment
from tools.signals.bands import get_bollinger_bands_signal
from tools.signals.macd import get_macd_signal
from tools.signals.rsi import get_rsi_signal
from tools.signals.sma import get_sma_crossover_signal
from tools.signals.vix import get_vix_market_fear_signal
from utils.prompt import SYSTEM_PROMPT


def create_finance_agent() -> Agent:
    return Agent(
        model=Gemini(id=GOOGLE_MODEL_NAME_1, api_key=GOOGLE_API_KEY_2, seed=42),
        tools=[
            YFinanceTools(),
            get_sma_crossover_signal,
            get_rsi_signal,
            get_macd_signal,
            get_bollinger_bands_signal,
            get_vix_market_fear_signal,
        ],
        exponential_backoff=True,
        delay_between_retries=3,
        expected_output='You are expected to give the summary of all the techincal indicators in proper format and make sure to come to a conclusion with it.',
        instructions=[
            'Role: You are a Quantitative Analyst. Your analysis is strictly objective and data-based.',
            'Task: Execute all available technical analysis tools for the given stock ticker.',
            'Process: For each tool, determine the signal (Bullish, Bearish, Neutral) and provide a one-sentence data-driven justification.',
        ],
        markdown=True,
        name='Finance_Agent',
        id='agent_1',
        # enable_agentic_memory=True,
        # enable_user_memories=True,
        user_id=DEFAULT_USER_ID,
        session_id=DEFAULT_SESSION_ID,
        debug_mode=DEBUG_MODE,
        debug_level=DEBUG_LEVEL,
        # db=db,
    )


def create_sentiment_agent() -> Agent:
    return Agent(
        name='Sentiment_Agent',
        id='agent_2',
        model=Gemini(id=GOOGLE_MODEL_NAME_1, api_key=GOOGLE_API_KEY_1, seed=42),
        instructions=[
            'Role: You are a Market Sentiment Analyst.',
            'Task: For a given stock ticker, you must use ALL available sentiment tools (Reddit, FinHub News, DuckDuckGo, Google Search) to gather market sentiment data. Do not skip any tool.',
            'Process: For each tool, extract the sentiment signal, confidence, justification, and key headlines or points. Aggregate the results from all tools, identifying consensus and divergence. Ignore irrelevant or off-topic results.',
        ],
        tools=[
            get_reddit_sentiment,
            get_finnhub_news_sentiment,
            DuckDuckGoTools(fixed_max_results=10, timeout=30),
            GoogleSearchTools(fixed_max_results=10, timeout=30),
        ],
        markdown=True,
        exponential_backoff=True,
        delay_between_retries=3,
        user_id=DEFAULT_USER_ID,
        session_id=DEFAULT_SESSION_ID,
        # enable_agentic_memory=True,
        # enable_user_memories=True,
        debug_mode=DEBUG_MODE,
        debug_level=DEBUG_LEVEL,
        # db=db,
    )


def create_team() -> Team:
    finance_agent: Agent = create_finance_agent()
    sentiment_agent: Agent = create_sentiment_agent()

    return Team(
        id='team_1',
        name='PersonaQuantTeam',
        model=Gemini(
            id=GOOGLE_MODEL_NAME_1,
            api_key=GOOGLE_API_KEY_0,
            seed=42,
            system_prompt=SYSTEM_PROMPT,
        ),
        instructions=[
            "Identity: You are 'PersonaQuant,' the Lead Strategist.",
            'Objective: Formulate a coherent investment thesis by integrating agent reports.',
            'Execution Plan:',
            '1. Delegate: Task Finance_Agent for technicals and Sentiment_Agent for sentiment.',
            '2. Synthesize: Critically compare the two reports. Identify convergence (confirmation) and divergence (conflict).',
            '3. Conclude: Formulate a final recommendation. Technicals are the primary factor; sentiment is the secondary/confirming factor. State the final thesis clearly.',
        ],
        exponential_backoff=True,
        delay_between_retries=3,
        reasoning=REASONING_MODE,
        # reasoning_max_steps=3,
        # markdown=True,
        members=[finance_agent, sentiment_agent],
        # db=db,
        user_id=DEFAULT_USER_ID,
        session_id=DEFAULT_SESSION_ID,
        # add_history_to_context=True,
        # num_history_runs=5,
        # enable_session_summaries=True,
        # enable_agentic_memory=True,
        # enable_user_memories=True,
        # add_session_summary_to_context=True,
        # add_memories_to_context=True,
        debug_mode=DEBUG_MODE,
        debug_level=DEBUG_LEVEL,
    )


team: Team = create_team()
