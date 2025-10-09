from agno.agent import Agent
from agno.models.google import Gemini
from agno.team import Team
from agno.tools.calculator import CalculatorTools
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools

from config import (
    DEBUG_LEVEL,
    DEBUG_MODE,
    DEFAULT_SESSION_ID,
    DEFAULT_USER_ID,
    GOOGLE_API_KEY_0,
    GOOGLE_API_KEY_1,
    GOOGLE_API_KEY_2,
    GOOGLE_MODEL_NAME_1,
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
        description='You are a Finance Agent who analyzes technical indicators and explains them in simple terms.',
        model=Gemini(id=GOOGLE_MODEL_NAME_1, api_key=GOOGLE_API_KEY_1, seed=42),
        instructions=[
            '1. Role: Analyze technical indicators and translate them into plain English.',
            '2. Tools: Use SMA, RSI, MACD, Bollinger Bands, Ichimoku, Fibonacci, OBV, and VIX.',
            '3. Think Strategically: Technical signals can be misleading. A stock showing "oversold" might be falling for good reasons (bad fundamentals). Always consider:',
            '   - Are all indicators aligned or conflicting?',
            '   - Is this a short-term fluctuation or a trend reversal?',
            '   - Does high volatility suggest opportunity or danger?',
            '4. Keep It Simple: Avoid jargon. Say "price trending up" not "bullish momentum". Say "oversold" as "potentially undervalued".',
            '5. For Each Ticker: Provide clear BUY/SELL/HOLD signal based on indicators, but note any conflicting signals.',
            '6. Key Levels: Always show support (floor price) and resistance (ceiling price) in dollars.',
            '7. Market Context: Explain VIX in simple terms - "Low fear = stable market" or "High fear = volatile market".',
            '8. Missing Data: If indicator unavailable, state which one and work with what you have.',
            '9. Format: Follow FINANCE_AGENT_OUTPUT exactly - keep table concise.',
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
                exclude_tools=[
                    'get_technical_indicators',
                    'get_historical_stock_prices',
                    'get_income_statements',
                ]
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
        db=db,
    )


def create_sentiment_agent() -> Agent:
    return Agent(
        name='Sentiment_Agent',
        id='agent_2',
        description='You are a Sentiment Agent who gauges what people are saying about stocks.',
        model=Gemini(id=GOOGLE_MODEL_NAME_1, api_key=GOOGLE_API_KEY_2, seed=42),
        instructions=[
            '1. Role: Gauge market sentiment from news, social media, and financial sources.',
            '2. Tools: Use Reddit, Finnhub news, and YFinance news sentiment.',
            '3. Think Critically: Hype ≠ Good Investment. A stock with 100% positive sentiment might be overvalued and due for correction. Consider:',
            '   - Is positive sentiment based on fundamentals or just hype/FOMO?',
            '   - Are negative headlines about temporary issues or systemic problems?',
            '   - Does extreme sentiment (very positive or negative) suggest the move is already priced in?',
            '4. For Indian Stocks (.NS, .BO, .BSE): Prioritize YFinance news as Reddit/Finnhub may have limited coverage.',
            '5. Score: Provide 0-100 sentiment score and clear Bullish/Bearish/Neutral label.',
            '6. Headlines: Show actual headlines/themes found, not invented content.',
            '7. Keep It Real: If no data for a source, state "No {source} data available" and work with what you have.',
            '8. Bottom Line: One sentence summary of overall market mood with caveat if sentiment seems excessive.',
            '9. Format: Follow SENTIMENT_AGENT_OUTPUT - be factual and concise.',
        ],
        expected_output=SENTIMENT_AGENT_OUTPUT,
        tools=[
            get_reddit_sentiment,
            get_finnhub_news_sentiment,
            get_yfinance_news_sentiment,
            # DuckDuckGoTools(
            #     enable_search=True, enable_news=True, fixed_max_results=10, timeout=30
            # ),
        ],
        markdown=True,
        exponential_backoff=True,
        delay_between_retries=3,
        user_id=DEFAULT_USER_ID,
        session_id=DEFAULT_SESSION_ID,
        debug_mode=DEBUG_MODE,
        debug_level=DEBUG_LEVEL,
        db=db,
    )


def create_advisory_agent() -> Agent:
    return Agent(
        name='Advisory_Agent',
        id='agent_3',
        model=Gemini(id=GOOGLE_MODEL_NAME_1, api_key=GOOGLE_API_KEY_1, seed=42),
        description='You are an Advisory Agent who tests investment strategies and recommends the best approach.',
        instructions=[
            '1. Role: Test multiple investment strategies and recommend the best one based on data.',
            '2. Always Call: backtest_investment_strategies AND build_portfolio_allocation (both tools).',
            '3. Think Strategically: Past performance ≠ Future results. Consider:',
            '   - Does the winning strategy fit the current market conditions?',
            '   - Is high past return due to luck or repeatable patterns?',
            '   - Does the strategy align with user risk tolerance even if not highest return?',
            '   - Are we in a different market regime (bull vs bear) than the backtest period?',
            '4. Extract From User Query:',
            '   - Capital: ₹50,000 or $10k → extract amount',
            '   - Risk: "minimal/low risk" → conservative, "moderate" → moderate, "aggressive/high growth" → aggressive',
            '   - Timeline: "short" → 1yr, "medium" → 3yr, "long" → 5yr',
            '   - Broker: zerodha, groww, upstox, robinhood, fidelity, etc.',
            '5. Show All 4 Strategies: Buy & Hold, DCA, SMA Crossover, RSI Mean Reversion with their performance.',
            '6. Explain Simply: "Risk Score" instead of "Sharpe Ratio", "Max Loss" instead of "Max Drawdown".',
            '7. Be Specific: Give exact dollar amounts, percentages, and action steps.',
            '8. Handle Failures: If tool fails, state which one and provide basic guidance based on risk profile.',
            '9. Format: Follow ADVISOR_AGENT_OUTPUT - keep it concise and actionable.',
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
        db=db,
    )


def create_search_agent() -> Agent:
    return Agent(
        name='Search_Agent',
        id='agent_4',
        model=Gemini(id=GOOGLE_MODEL_NAME_1, api_key=GOOGLE_API_KEY_0, seed=42),
        description='You are a Search Agent who finds latest news and developments about stocks.',
        instructions=[
            '1. Role: Find recent news and developments that could impact stock prices.',
            '2. Tools: Use LinkUp AI and DuckDuckGo search.',
            '3. Think Critically: Not all news is equally important. A viral tweet ≠ material change. Consider:',
            '   - Is this news about actual business performance or just market noise?',
            '   - Will this impact matter in 1 year or just 1 week?',
            '   - Are positive headlines hiding negative fundamentals (or vice versa)?',
            '   - Is the market overreacting or underreacting to this development?',
            '4. Search Strategy: Use company name + relevant keywords (not just ticker) for better results.',
            '5. For Each Development: Note impact (Positive/Negative/Neutral) and timing if available.',
            '6. Focus on Catalysts: Prioritize news that could actually move the stock (earnings, product launches, regulations, etc.).',
            '7. Be Honest: If search returns limited results, say so.',
            '8. Key Takeaway: One sentence on what matters most for long-term investors.',
            '9. Format: Follow SEARCH_AGENT_OUTPUT - keep it brief and factual.',
        ],
        expected_output=SEARCH_AGENT_OUTPUT,
        tools=[
            # LinkupTools(
            #     api_key=LINKUP_API_KEY, depth='standard', output_type='searchResults'
            # ),
            DuckDuckGoTools(
                enable_search=True, enable_news=True, fixed_max_results=100, timeout=30
            )
        ],
        markdown=True,
        exponential_backoff=True,
        delay_between_retries=3,
        user_id=DEFAULT_USER_ID,
        session_id=DEFAULT_SESSION_ID,
        debug_mode=DEBUG_MODE,
        debug_level=DEBUG_LEVEL,
        db=db,
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
            '1. Identify Tickers: If user provides ticker, use it. If not, suggest 1-3 relevant tickers.',
            '2. Format Tickers: Indian stocks need .NS suffix (e.g., HDFC.NS). US stocks as-is (e.g., NVDA).',
            '3. Execute Sequence:',
            '   Step 1: Search_Agent → Find recent news',
            '   Step 2: Finance_Agent → Analyze technical indicators',
            '   Step 3: Sentiment_Agent → Check market mood',
            '   Step 4: Advisory_Agent → Test strategies and recommend',
            '4. Wait for All: Collect all agent responses before creating final report.',
            '5. Synthesize Strategically: Your job is to balance all perspectives. Consider:',
            '   - If technicals say BUY but sentiment is extreme hype → might be overvalued',
            '   - If news is negative but technicals strong → might be buying opportunity',
            '   - If all signals agree → higher confidence',
            '   - If signals conflict → note the disagreement and explain why',
            '6. Final Report Should Be:',
            '   - Brief executive summary showing the balanced view',
            '   - Clear recommendation (BUY/SELL/HOLD) with confidence level',
            '   - One summary table combining all signals',
            '   - Specific action steps based on the complete picture',
            '   - Simple language (avoid jargon)',
            '   - Note any risks or caveats (e.g., "High sentiment may mean already priced in")',
            '7. Handle Missing Data:',
            '   - If agent fails, note which one in final report',
            '   - Provide best recommendation with available data',
            '   - Lower confidence if critical data missing',
            '8. Follow FINAL_OUTPUT_FORMAT exactly - keep it concise and actionable.',
        ],
        expected_output=FINAL_OUTPUT_FORMAT,
        exponential_backoff=True,
        delay_between_retries=3,
        reasoning=REASONING_MODE,
        markdown=True,
        members=[finance_agent, sentiment_agent, advisory_agent, search_agent],
        user_id=DEFAULT_USER_ID,
        session_id=DEFAULT_SESSION_ID,
        debug_mode=DEBUG_MODE,
        debug_level=DEBUG_LEVEL,
        db=db,
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
