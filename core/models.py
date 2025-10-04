from enum import Enum

from pydantic import BaseModel, Field


class MarketSignal(str, Enum):
    BUY = 'buy'
    SELL = 'sell'
    HOLD = 'hold'


class SentimentScore(BaseModel):
    score: float = Field(
        ..., description='Sentiment score between -1 (negative) and 1 (positive)'
    )
    source: str = Field(..., description='Source of sentiment (reddit, finnhub, etc.)')
    confidence: float = Field(..., description='Confidence level of sentiment analysis')


class TechnicalIndicator(BaseModel):
    indicator_name: str = Field(
        ..., description='Name of technical indicator (RSI, MACD, etc.)'
    )
    value: float = Field(..., description='Current indicator value')
    signal: MarketSignal = Field(..., description='Trading signal from indicator')
    timestamp: str = Field(..., description='When indicator was calculated')


class PortfolioAllocation(BaseModel):
    ticker: str = Field(..., description='Stock ticker symbol')
    allocation_percentage: float = Field(
        ..., description='Recommended allocation percentage'
    )
    rationale: str = Field(..., description='Reasoning for allocation')


class FinancialAnalysis(BaseModel):
    ticker: str = Field(
        ..., description='Stock ticker symbol (append .NS/.BSE for Indian stocks)'
    )
    company_name: str = Field(..., description='Full company name')
    current_price: float = Field(..., description='Current stock price')
    technical_signals: list[TechnicalIndicator] = Field(
        ..., description='Technical analysis indicators'
    )
    sentiment_analysis: list[SentimentScore] = Field(
        ..., description='Market sentiment from various sources'
    )
    portfolio_recommendation: list[PortfolioAllocation] = Field(
        ..., description='Portfolio allocation suggestions'
    )
    market_fear_index: float | None = Field(
        None, description='VIX fear index if available'
    )
    summary: str = Field(..., description='Brief summary explained in easier terms')
    recommendation: MarketSignal = Field(
        ..., description='Overall trading recommendation'
    )
