from typing import Literal, Optional

from pydantic import BaseModel, Field


class TechnicalIndicator(BaseModel):
    """Individual technical indicator result"""

    name: str = Field(..., description='Indicator name (e.g., RSI, MACD, SMA)')
    signal: str = Field(
        ..., description='Trading signal (e.g., Bullish, Bearish, Neutral)'
    )
    value: Optional[str] = Field(None, description='Current indicator value or range')
    confidence: Optional[str] = Field(
        None, description='Confidence level (High, Medium, Low)'
    )


class FinancialMetrics(BaseModel):
    """Key financial metrics for the stock"""

    current_price: float = Field(..., description='Current stock price')
    pe_ratio: Optional[float] = Field(None, description='Price-to-Earnings ratio')
    market_cap: Optional[str] = Field(None, description='Market capitalization')
    dividend_yield: Optional[float] = Field(
        None, description='Dividend yield percentage'
    )


class FinanceAgentOutput(BaseModel):
    """Finance Agent's technical and fundamental analysis output"""

    ticker: str = Field(..., description='Stock ticker symbol')
    technical_indicators: list[TechnicalIndicator] = Field(
        ..., description='List of technical indicator signals'
    )
    financial_metrics: FinancialMetrics = Field(
        ..., description='Key financial metrics'
    )
    market_context: str = Field(
        ..., description='Overall market context (e.g., VIX level, market sentiment)'
    )
    technical_summary: str = Field(
        ..., description='Brief summary of technical outlook'
    )


class SentimentSource(BaseModel):
    """Sentiment data from a single source"""

    source: str = Field(..., description='Source name (Reddit, Finnhub, YFinance)')
    sentiment: Literal['positive', 'negative', 'neutral', 'unavailable'] = Field(
        ..., description='Overall sentiment classification'
    )
    score: Optional[float] = Field(
        None, ge=-1, le=1, description='Sentiment score (-1 to 1)'
    )
    key_themes: list[str] = Field(
        default_factory=list, description='Main themes or topics discussed'
    )
    sample_headlines: list[str] = Field(
        default_factory=list, description='Top 3-5 representative headlines'
    )


class SentimentAgentOutput(BaseModel):
    """Sentiment Agent's market sentiment analysis output"""

    ticker: str = Field(..., description='Stock ticker symbol')
    overall_sentiment: Literal['bullish', 'bearish', 'neutral', 'mixed'] = Field(
        ..., description='Aggregated market sentiment'
    )
    sentiment_score: float = Field(
        ..., ge=-1, le=1, description='Overall sentiment score (-1 to 1)'
    )
    sources: list[SentimentSource] = Field(
        ..., description='Sentiment breakdown by source'
    )
    sentiment_summary: str = Field(
        ..., description='Brief summary of sentiment findings'
    )


class StrategyPerformance(BaseModel):
    """Performance metrics for a backtested strategy"""

    strategy_name: str = Field(..., description='Strategy name')
    annual_return_pct: float = Field(..., description='Annualized return percentage')
    sharpe_ratio: float = Field(..., description='Risk-adjusted return metric')
    max_drawdown_pct: float = Field(..., description='Maximum drawdown percentage')


class PositionRecommendation(BaseModel):
    """Specific position recommendation for a ticker"""

    ticker: str = Field(..., description='Stock ticker symbol')
    recommended_shares: int = Field(..., description='Number of shares to buy')
    allocation_pct: float = Field(..., description='Percentage of portfolio')
    entry_price: float = Field(..., description='Recommended entry price')
    stop_loss_price: Optional[float] = Field(None, description='Stop-loss price level')


class AdvisoryAgentOutput(BaseModel):
    """Advisory Agent's portfolio and strategy recommendations"""

    capital: float = Field(..., description='Total investment capital')
    risk_profile: str = Field(
        ..., description='Risk profile (conservative, moderate, aggressive)'
    )
    recommended_strategy: str = Field(
        ..., description='Best strategy based on backtest'
    )
    strategy_rationale: str = Field(..., description='Why this strategy is recommended')
    backtested_strategies: list[StrategyPerformance] = Field(
        ..., description='Performance comparison of strategies'
    )
    portfolio_positions: list[PositionRecommendation] = Field(
        ..., description='Specific position recommendations'
    )
    advisory_summary: str = Field(
        ..., description='Overall advisory recommendation summary'
    )


class NewsItem(BaseModel):
    """Individual news or web search result"""

    title: str = Field(..., description='News headline or result title')
    source: str = Field(..., description='Source website or publication')
    summary: Optional[str] = Field(None, description='Brief summary of content')
    relevance: Optional[str] = Field(
        None, description='Relevance to query (high, medium, low)'
    )


class SearchAgentOutput(BaseModel):
    """Search Agent's web research and news findings"""

    query: str = Field(..., description='Search query used')
    recent_news: list[NewsItem] = Field(
        default_factory=list, description='Recent news articles found'
    )
    key_findings: list[str] = Field(..., description='Key insights from web research')
    search_summary: str = Field(..., description='Summary of search findings')


class AgentSummary(BaseModel):
    """Summary of individual agent's contribution"""

    agent_name: str = Field(
        ..., description='Agent name (Finance, Sentiment, Advisory, Search)'
    )
    key_findings: str = Field(
        ..., description="Concise summary of agent's main findings"
    )


class TeamOutput(BaseModel):
    """Final consolidated output from the entire team"""

    executive_summary: str = Field(
        ..., description='High-level overview of the analysis'
    )
    ticker_analyzed: str = Field(..., description='Primary stock ticker analyzed')
    agent_summaries: list[AgentSummary] = Field(
        ..., description='Summary from each agent'
    )
    key_takeaways: list[str] = Field(
        ...,
        description='3-5 actionable insights from the analysis',
        min_length=3,
        max_length=5,
    )
    final_recommendation: str = Field(
        ..., description='Overall investment perspective and guidance'
    )
    risk_disclaimer: str = Field(
        default='This analysis is for educational purposes only and not financial advice. Consult a licensed financial advisor before making investment decisions.',
        description='Risk disclaimer',
    )
