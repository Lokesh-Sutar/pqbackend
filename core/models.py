from enum import Enum
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, HttpUrl


class MarketSignal(str, Enum):
    BUY = 'buy'
    SELL = 'sell'
    HOLD = 'hold'


class Indicator(BaseModel):
    indicator_name: str = Field(
        ..., description='Name of the technical indicator (e.g., RSI, MACD)'
    )
    value: float = Field(..., description='Numeric value of the indicator')
    signal: Literal['buy', 'hold', 'sell'] = Field(
        ..., description='Trading signal derived from the indicator'
    )
    explanation: str = Field(..., description='Explanation of what the indicator implies')


class KeyFinancialRatios(BaseModel):
    trailingPE: float = Field(
        ..., description='Price-to-Earnings ratio based on trailing 12 months'
    )
    forwardPE: float = Field(..., description='Projected Price-to-Earnings ratio')
    priceToBook: float = Field(
        ..., description='Market price divided by book value per share'
    )
    dividendYield: float = Field(..., description='Dividend yield as a percentage')
    returnOnEquity: float = Field(
        ..., description='Profitability relative to shareholders’ equity'
    )
    debtToEquity: float = Field(
        ..., description='Leverage ratio measuring financial risk'
    )


class StockAnalysis(BaseModel):
    indicators: list[Indicator]
    current_stock_price: float = Field(
        ..., description='Current market price of the stock'
    )
    key_financial_ratios: KeyFinancialRatios


class Headline(BaseModel):
    title: str = Field(..., description='Headline or post title related to the asset')
    source_url: Optional[HttpUrl] = Field(None, description='Link to the article or post')
    sentiment: Literal['positive', 'neutral', 'negative'] = Field(
        ..., description='Headline sentiment classification'
    )


class SentimentSource(BaseModel):
    source_name: Literal['Reddit', 'Finhub', 'YahooFinance', 'WebSearch'] = Field(
        ..., description='Name of the sentiment data source'
    )
    sentiment_score: float = Field(
        ..., ge=-1, le=1, description='Overall sentiment score (-1 to 1)'
    )
    top_headlines: list[Headline] = Field(
        ..., description='Top 5 relevant headlines or posts with sentiment analysis'
    )


class SentimentAnalysis(BaseModel):
    symbol: str = Field(..., description='Stock ticker symbol (e.g., AAPL, TSLA)')
    overall_sentiment: Literal['bullish', 'neutral', 'bearish'] = Field(
        ..., description='Aggregated market sentiment based on all sources'
    )
    sources: list[SentimentSource] = Field(
        ..., description='List of sentiment data from various platforms'
    )
    updated_at: Optional[str] = Field(
        None, description='Timestamp of the latest sentiment data'
    )


class PortfolioAllocation(BaseModel):
    ticker: str = Field(..., description='Stock ticker symbol')
    allocation_percentage: float = Field(
        ..., description='Recommended allocation percentage'
    )
    rationale: str = Field(..., description='Reasoning for allocation')
