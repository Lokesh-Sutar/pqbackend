from agno.agent import Agent
from agno.models.google import Gemini
from agno.team import Team
from agno.tools.calculator import CalculatorTools
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.linkup import LinkupTools
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
    LINKUP_API_KEY,
    OPENROUTER_MODEL_API,
    OPENROUTER_MODEL_NORMAL,
    REASONING_MODE,
    db,
)
from tools.advisory.backtester import backtest_investment_strategies
from tools.advisory.portfolio_builder import build_portfolio_allocation
from tools.sentiment.finhub import get_finnhub_news_sentiment
from tools.sentiment.reddit import get_reddit_sentiment
from tools.sentiment.yfinance import get_yfinance_news_sentiment
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
    SEARCH_AGENT_OUTPUT,
    SENTIMENT_AGENT_OUTPUT,
)


def create_finance_agent() -> Agent:
    return Agent(
        name='Finance_Agent',
        id='agent_1',
        description='You are a Finance Agent who is going to analyze the key financials and technical indicators of a company.',
        model=Gemini(id=GOOGLE_MODEL_NAME_1, api_key=GOOGLE_API_KEY_2, seed=42),
        instructions=[
            '1. Role Definition: You are a Finance Agent specializing in technical and quantitative stock analysis.',
            '2. Task: Analyze the key financial and technical indicators of a company using the available tools.',
            '3. Tools: Use SMA, RSI, MACD, Bollinger Bands, Ichimoku Cloud, Fibonacci Retracement, OBV, and VIX for comprehensive momentum and trend analysis.',
            '4. Context: Use the VIX signal to provide broader market sentiment context.',
            '5. Scope: Do not give investment advice; interpret technicals objectively.',
            '6. Output Format Rule: You must strictly follow the expected_output format exactly as shown. Do not add commentary, markdown, or omit any section. Keep identical headers and indentation.',
        ],
        # parser_model=Gemini(id=GOOGLE_MODEL_NAME_0, api_key=GOOGLE_API_KEY_1, seed=42),
        # parser_model_prompt='You must strictly follow the expected_output format exactly as shown. Do not add commentary, markdown, or omit any section. Keep identical headers and indentation.',
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
            '1. Role Definition: You are a Sentiment Market Agent analyzing public and media sentiment for a company or stock ticker.',
            '2. Task: Gather sentiment data from Reddit, financial news (Finnhub), YFinance news, and general web searches.',
            '3. Tool Selection: Use YFinance sentiment tool for Indian stocks (tickers with .NS, .BSE, .BO suffixes) as Reddit and Finnhub may not have coverage for these stocks.',
            "4. Evaluation: Summarize tone and recurring themes. If a source has no relevant data, explicitly state 'Data not available.'",
            '5. Consolidation: Produce a single overall sentiment score or qualitative label (e.g., Positive, Neutral, Negative).',
            '6. Restriction: Do not invent or assume sentiment data.',
            '7. Output Format Rule: Strictly follow the expected_output format. Preserve structure, indentation, and section headers exactly.',
        ],
        # parser_model=Gemini(id=GOOGLE_MODEL_NAME_0, api_key=GOOGLE_API_KEY_2, seed=42),
        # parser_model_prompt='You must strictly follow the expected_output format exactly as shown. Do not add commentary, markdown, or omit any section. Keep identical headers and indentation.',
        expected_output=SENTIMENT_AGENT_OUTPUT,
        tools=[
            get_reddit_sentiment,
            get_finnhub_news_sentiment,
            get_yfinance_news_sentiment,
            # DuckDuckGoTools(
            #     enable_search=True, enable_news=True, fixed_max_results=10, timeout=30
            # ),
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
            '1. Role Definition: You are an Advisory Agent and quantitative financial strategist.',
            '2. Task: Always call backtest_investment_strategies and build_portfolio_allocation tools to run them.',
            '3. User Data: If user didn\'t provide any data, assume a risk tolerance of "moderate" and an investment horizon of "1-3 years" and capital of $10,000 in US Markets.',
            '4. Evidence: Every recommendation must be justified with backtesting or portfolio metrics.',
            "5. Clarity: When data or simulation fails, explicitly state 'Data not available' or 'Insufficient data to simulate.'",
            '6. Guidance: Provide analysis, not investment advice.',
            '7. Output Format Rule: You must match the expected_output format exactly — same headers, indentation, and labels.',
        ],
        # parser_model=Gemini(id=GOOGLE_MODEL_NAME_0, api_key=GOOGLE_API_KEY_0, seed=42),
        # parser_model_prompt='You must strictly follow the expected_output format exactly as shown. Do not add commentary, markdown, or omit any section. Keep identical headers and indentation.',
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


def create_search_agent() -> Agent:
    return Agent(
        name='Search_Agent',
        id='agent_4',
        model=Gemini(id=GOOGLE_MODEL_NAME_1, api_key=GOOGLE_API_KEY_1, seed=42),
        description='You are a Search Agent who is going to fetch latest, new and relevant information from the web.',
        instructions=[
            '1. Role Definition: You are a Search Agent specializing in gathering accurate and relevant information from the web.',
            '2. Task: Use web search tools to find information based on user queries.',
            '3. Tool Selection: First call LinkUp AI Search and then call DuckDuckGo tools to retrieve the most relevant results.',
            '4. Evaluation: Summarize the findings clearly and concisely. If no relevant data is found, explicitly state "Data not available."',
            "5. For LinkupTool make sure to query using different keywords alongside company name. Don't just search ticker as it may not return relevant results.",
        ],
        # parser_model=Gemini(id=GOOGLE_MODEL_NAME_1, api_key=GOOGLE_API_KEY_2, seed=42),
        # parser_model_prompt='You must strictly follow the expected_output format exactly as shown. Do not add commentary, markdown, or omit any section. Keep identical headers and indentation.',
        expected_output=SEARCH_AGENT_OUTPUT,
        tools=[
            LinkupTools(
                api_key=LINKUP_API_KEY, depth='standard', output_type='searchResults'
            ),
            DuckDuckGoTools(
                enable_search=True, enable_news=True, fixed_max_results=10, timeout=30
            ),
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
    search_agent: Agent = create_search_agent()

    return Team(
        id='team_1',
        name='PersonaQuantTeam',
        model=Gemini(id=GOOGLE_MODEL_NAME_1, api_key=GOOGLE_API_KEY_1, seed=42),
        instructions=[
            '1. Ticker Identification: Detect if the user provides a stock ticker. If not, infer 1-3 suitable tickers for analysis.',
            "2. Ticker Formatting: For Indian stocks, format tickers with exchange suffix '.NS' if the specific exchange is unknown.",
            '3. Efficient Data Gathering: For each ticker, retrieve sentiment, financials, and advisory data simultaneously.',
            "4. Missing Data Handling: If any agent returns incomplete data, keep the process running and label the missing fields clearly as 'Data not available'.",
            '5. Output Integration: Merge all agent results into a unified final report.',
            '6. Format Enforcement: The final report must strictly follow FINAL_OUTPUT_FORMAT. Use identical section headers, markdown dividers, and indentation. Do not add explanations or narrative text outside the structure.',
        ],
        parser_model=Gemini(id=GOOGLE_MODEL_NAME_0, api_key=GOOGLE_API_KEY_1, seed=42),
        parser_model_prompt='You must strictly follow the expected_output format exactly as shown. Do not add commentary, markdown, or omit any section. Keep identical headers and indentation.',
        expected_output=FINAL_OUTPUT_FORMAT,
        exponential_backoff=True,
        delay_between_retries=3,
        reasoning=REASONING_MODE,
        markdown=True,
        members=[search_agent, finance_agent, sentiment_agent, advisory_agent],
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
