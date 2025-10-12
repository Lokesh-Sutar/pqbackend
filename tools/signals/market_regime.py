"""
Market Regime Detection Tool
Identifies current market conditions (Bull/Bear/Sideways/Volatile) to adapt strategy
"""

import logging
from typing import Any, Dict

import numpy as np
import yfinance as yf
from agno.tools import tool

logger: logging.Logger = logging.getLogger(__name__)


@tool(
    name='detect_market_regime',
    description='Detects current market regime (bull/bear/sideways/volatile) to adapt investment strategy',
)
def detect_market_regime(ticker: str, lookback_days: int = 90) -> Dict[str, Any]:
    """
    Detect market regime for a stock using trend, volatility, and momentum analysis

    Args:
        ticker: Stock symbol (e.g., 'AAPL', 'RELIANCE.NS')
        lookback_days: Days to analyze (default 90 for 3 months)

    Returns:
        Dict with regime classification and metrics
    """

    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=f'{lookback_days}d')

        if hist.empty or len(hist) < 20:
            return {
                'signal': 'Insufficient Data',
                'ticker': ticker,
                'error': f'Need at least 20 days of data, got {len(hist)}',
            }

        closes = hist['Close']
        current_price = closes.iloc[-1]

        sma_20 = closes.rolling(window=20).mean().iloc[-1]
        sma_50 = closes.rolling(window=min(50, len(closes))).mean().iloc[-1]

        price_vs_sma20 = ((current_price - sma_20) / sma_20) * 100
        price_vs_sma50 = ((current_price - sma_50) / sma_50) * 100

        returns = closes.pct_change().dropna()
        cumulative_return = ((current_price - closes.iloc[0]) / closes.iloc[0]) * 100

        volatility = returns.std() * np.sqrt(252) * 100  # Annualized volatility

        highs = hist['High']
        lows = hist['Low']
        price_range = ((highs.max() - lows.min()) / lows.min()) * 100

        regime = ''
        regime_confidence = 0.0
        characteristics = []
        recommendation = ''

        if price_vs_sma20 > 2 and price_vs_sma50 > 5 and cumulative_return > 10:
            regime = 'Bull Market'
            regime_confidence = min(95, 60 + abs(cumulative_return))
            characteristics = [
                'Price above moving averages',
                f'Strong uptrend (+{cumulative_return:.1f}%)',
                'Momentum is positive',
            ]
            recommendation = 'Favor momentum strategies (buy the dip). Consider taking partial profits if overextended.'

        elif price_vs_sma20 < -2 and price_vs_sma50 < -5 and cumulative_return < -10:
            regime = 'Bear Market'
            regime_confidence = min(95, 60 + abs(cumulative_return))
            characteristics = [
                'Price below moving averages',
                f'Strong downtrend ({cumulative_return:.1f}%)',
                'Negative momentum',
            ]
            recommendation = 'Avoid buying. Consider shorting or cash position. Wait for reversal signals.'

        elif volatility > 40:
            regime = 'High Volatility'
            regime_confidence = min(90, 50 + volatility)
            characteristics = [
                f'Extreme volatility ({volatility:.1f}% annualized)',
                f'Large price swings ({price_range:.1f}% range)',
                'Unpredictable movements',
            ]
            recommendation = 'Reduce position size. Use wider stop-losses. Consider options strategies or sit out.'

        elif abs(cumulative_return) < 5 and price_range < 20:
            regime = 'Sideways/Consolidation'
            regime_confidence = 70
            characteristics = [
                f'Flat performance ({cumulative_return:+.1f}%)',
                'Price in narrow range',
                'No clear trend',
            ]
            recommendation = 'Range trading strategies. Buy support, sell resistance. Await breakout.'

        elif cumulative_return > 0 and price_vs_sma20 > 0:
            regime = 'Mild Bull Market'
            regime_confidence = 65
            characteristics = [
                f'Modest uptrend (+{cumulative_return:.1f}%)',
                'Price above short-term average',
                'Positive but weak momentum',
            ]
            recommendation = 'Can hold or add cautiously. Watch for pullbacks to enter. Not overheated yet.'

        elif cumulative_return < 0 and price_vs_sma20 < 0:
            regime = 'Mild Bear Market'
            regime_confidence = 65
            characteristics = [
                f'Modest downtrend ({cumulative_return:.1f}%)',
                'Price below short-term average',
                'Weak negative momentum',
            ]
            recommendation = 'Consider lightening positions. Not panic-sell territory but be cautious.'

        else:
            regime = 'Uncertain/Transitioning'
            regime_confidence = 50
            characteristics = [
                'Mixed signals from indicators',
                'Possible regime change in progress',
                'Wait for clearer picture',
            ]
            recommendation = (
                'Stay on sidelines or use small positions. Market direction unclear.'
            )

        result = {
            'signal': regime,
            'ticker': ticker,
            'confidence': regime_confidence,
            'details': {
                'regime': regime,
                'lookback_period': f'{lookback_days} days',
                'current_price': float(round(current_price, 2)),
                'cumulative_return_pct': float(round(cumulative_return, 2)),
                'volatility_pct': float(round(volatility, 2)),
                'price_vs_sma20_pct': float(round(price_vs_sma20, 2)),
                'price_vs_sma50_pct': float(round(price_vs_sma50, 2)),
                'price_range_pct': float(round(price_range, 2)),
                'characteristics': characteristics,
                'recommendation': recommendation,
            },
            'interpretation': f'{ticker} is in a {regime} (confidence: {regime_confidence}%). {recommendation}',
        }

        return result

    except Exception as e:
        logger.error(f'Error detecting market regime for {ticker}: {e}')
        return {'signal': 'Error', 'ticker': ticker, 'error': str(e)}
