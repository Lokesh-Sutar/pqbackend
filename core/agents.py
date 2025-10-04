from agno.agent import Agent
from agno.models.google import Gemini
from agno.models.openrouter import OpenRouter
from agno.team import Team
from agno.tools.calculator import CalculatorTools
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
    GROQ_API_KEY,
    OPENROUTER_MODEL_API,
    OPENROUTER_MODEL_NORMAL,
    REASONING_MODE,
    db,
)
from core.models import FinancialAnalysis
from tools.advisory.backtester import backtest_investment_strategies
from tools.advisory.portfolio_builder import build_portfolio_allocation
from tools.sentiment.finhub import get_finnhub_news_sentiment
from tools.sentiment.reddit import get_reddit_sentiment
from tools.signals import (
    get_bollinger_bands_signal,
    get_fibonacci_retracement,
    get_ichimoku_cloud_signal,
    get_macd_signal,
    get_obv_signal,
    get_rsi_signal,
    get_sma_crossover_signal,
    get_vix_market_fear_signal,
)
from utils.prompt import (
    ADVISOR_AGENT_OUTPUT,
    FINAL_OUTPUT_FORMAT,
    FINANCE_AGENT_OUTPUT,
    SENTIMENT_AGENT_OUTPUT,
)


def create_finance_agent() -> Agent:
    return Agent(
        model=Gemini(id=GOOGLE_MODEL_NAME_1, api_key=GOOGLE_API_KEY_2, seed=42),
        description='You are a Finance Agent who is going to analyze the key financials and technical indicators of a company.',
        instructions=[
            '1. You are a technical analysis expert for a given stock ticker.',
            "2. Use all available technical indicator tools (SMA, RSI, MACD, Bollinger Bands) to analyze the stock's current momentum and trend.",
            '3. Use the VIX tool to assess the overall market sentiment (fear/greed) as context for your analysis.',
            '4. Synthesize the signals from all indicators into a single, coherent technical outlook.',
            '5. Do not provide financial advice. Your role is to interpret the technical data objectively.',
        ],
        expected_output=FINANCE_AGENT_OUTPUT,
        tools=[
            get_sma_crossover_signal,
            get_rsi_signal,
            get_macd_signal,
            get_bollinger_bands_signal,
            get_vix_market_fear_signal,
            get_fibonacci_retracement,
            get_ichimoku_cloud_signal,
            get_obv_signal,
            YFinanceTools(
                exclude_tools=['get_technical_indicators', 'get_historical_stock_prices']
            ),
            CalculatorTools(),
        ],
        exponential_backoff=True,
        delay_between_retries=3,
        markdown=True,
        name='Finance_Agent',
        id='agent_1',
        user_id=DEFAULT_USER_ID,
        session_id=DEFAULT_SESSION_ID,
        debug_mode=DEBUG_MODE,
        debug_level=DEBUG_LEVEL,
    )


def create_sentiment_agent() -> Agent:
    return Agent(
        name='Sentiment_Agent',
        id='agent_2',
        description='You are a Sentiment Market Agent who is going to fetch public movements and sentiment of a company or ticker.',
        model=Gemini(id=GOOGLE_MODEL_NAME_1, api_key=GOOGLE_API_KEY_1, seed=42),
        instructions=[
            '1. Your goal is to determine the overall market sentiment for a given stock ticker.',
            '2. Gather data from all available sources: Reddit, financial news (Finnhub), and general web searches.',
            '3. Analyze the tone and key themes from each source.',
            '4. If a source provides no relevant information, state that and exclude it from the final analysis.',
            '5. Combine the findings into a single, consolidated sentiment score or rating.',
        ],
        expected_output=SENTIMENT_AGENT_OUTPUT,
        tools=[
            get_reddit_sentiment,
            get_finnhub_news_sentiment,
            CalculatorTools(),
            DuckDuckGoTools(
                enable_search=True, enable_news=True, fixed_max_results=10, timeout=30
            ),
            # GoogleSearchTools(fixed_max_results=10, timeout=30),
        ],
        markdown=True,
        exponential_backoff=True,
        delay_between_retries=3,
        user_id=DEFAULT_USER_ID,
        session_id=DEFAULT_SESSION_ID,
        debug_mode=DEBUG_MODE,
        debug_level=DEBUG_LEVEL,
    )


def create_advisory_agent() -> Agent:
    return Agent(
        name='Advisory_Agent',
        id='agent_3',
        model=Gemini(id=GOOGLE_MODEL_NAME_1, api_key=GOOGLE_API_KEY_1, seed=42),
        description='You are a Advisory Agent who is going to run backtest on various strategies and give personalized position advise.',
        instructions=[
            'You are a quantitative financial advisor.',
            'You will either backtest an investment strategy or build a sample portfolio allocation.',
            'When backtesting, use the provided tools to run the simulation and report the key performance metrics.',
            'When building a portfolio, use the provided tickers and user goals (e.g., risk tolerance, time horizon) to suggest a diversified allocation.',
            'All recommendations must be justified with data from your tools.',
        ],
        expected_output=ADVISOR_AGENT_OUTPUT,
        tools=[
            backtest_investment_strategies,
            build_portfolio_allocation,
            CalculatorTools(),
        ],
        markdown=True,
        exponential_backoff=True,
        delay_between_retries=3,
        user_id=DEFAULT_USER_ID,
        session_id=DEFAULT_SESSION_ID,
        debug_mode=DEBUG_MODE,
        debug_level=DEBUG_LEVEL,
    )


def create_team() -> Team:
    finance_agent: Agent = create_finance_agent()
    sentiment_agent: Agent = create_sentiment_agent()
    advisory_agent: Agent = create_advisory_agent()

    return Team(
        id='team_1',
        name='PersonaQuantTeam',
        model=Gemini(id=GOOGLE_MODEL_NAME_1, api_key=GOOGLE_API_KEY_1, seed=42),
        instructions=[
            "1. Ticker Identification: First, check if the user has provided a stock ticker. If not, use the user's query to find 1-3 suitable tickers to analyze.",
            "2. Ticker Formatting: For any Indian stocks, correctly format the ticker with its exchange suffix. Prioritize '.NS' (National Stock Exchange) if the specific exchange is unknown.",
            '3. Efficient Data Gathering: Consolidate your data requests. For each ticker, make a single call to the agent to retrieve all required data points (sentiment, financials, technicals) simultaneously.',
            "4. Handling Missing Data: If any piece of information, such as sentiment, is not available, do not halt the process. Proceed with the available data and explicitly note 'Data not available' in the corresponding section of the final report.",
            '5. Always Trigger Report Agent to Write Detailed Report.',
        ],
        expected_output=FINAL_OUTPUT_FORMAT,
        exponential_backoff=True,
        delay_between_retries=3,
        reasoning=REASONING_MODE,
        markdown=True,
        members=[finance_agent, sentiment_agent, advisory_agent],
        user_id=DEFAULT_USER_ID,
        session_id=DEFAULT_SESSION_ID,
        debug_mode=DEBUG_MODE,
        debug_level=DEBUG_LEVEL,
    )


_team_instance: Team | None = None


def get_team() -> Team:
    """Get or create the team instance (lazy loading for fast startup)"""
    global _team_instance
    if _team_instance is None:
        import logging

        logger = logging.getLogger(__name__)
        logger.info('Creating agent team (first time only)...')
        _team_instance = create_team()
        logger.info('Agent team created successfully')
    return _team_instance
