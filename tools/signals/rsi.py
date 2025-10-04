from typing import Any

import numpy as np
import pandas as pd
import talib
from agno.tools import tool
from pandas import DataFrame

from tools.helper import get_ticker, logger_hook, validate_data


@tool(
    name='get_rsi_signal',
    description='This tool analyzes the stock data for RSI signals using TA-Lib.',
    tool_hooks=[logger_hook],
)
def get_rsi_signal(ticker: str) -> dict[str, Any]:
    """
    Analyze Relative Strength Index (RSI) for a stock ticker.

    Args:
        ticker: Stock ticker symbol (e.g., 'NVDA', 'AAPL')

    Returns:
        dict with RSI analysis including tool name, signal type (Overbought/Oversold/Neutral),
        confidence level, justification, and RSI details
    """
    df: DataFrame = get_ticker(ticker=ticker)

    period = 14

    validation_error = validate_data(df, ['close'], period + 1, 'RSI')
    if validation_error:
        return validation_error

    close_prices = df['close'].values.astype(float)
    rsi_values = talib.RSI(close_prices, timeperiod=period)

    latest_rsi = rsi_values[-1]

    if np.isnan(latest_rsi):
        return {
            'tool': 'RSI',
            'description': 'This tool analyzes the stock data for RSI signals using TA-Lib.',
            'signal': 'Insufficient Data',
            'justification': 'Not enough data to calculate RSI',
            'details': {},
        }

    divergence_signal = None
    if len(close_prices) >= 30 and len(rsi_values) >= 30:
        recent_prices = close_prices[-30:]
        recent_rsi = rsi_values[-30:]

        valid_mask = ~np.isnan(recent_rsi)
        if np.sum(valid_mask) >= 20:
            recent_prices_valid = recent_prices[valid_mask]
            recent_rsi_valid = recent_rsi[valid_mask]

            price_trend = np.polyfit(
                range(len(recent_prices_valid)), recent_prices_valid, 1
            )[0]
            rsi_trend = np.polyfit(range(len(recent_rsi_valid)), recent_rsi_valid, 1)[0]

            if price_trend > 0 and rsi_trend < 0 and latest_rsi > 50:
                divergence_signal = 'Bearish Divergence (prices making higher highs while RSI makes lower highs)'
            elif price_trend < 0 and rsi_trend > 0 and latest_rsi < 50:
                divergence_signal = 'Bullish Divergence (prices making lower lows while RSI makes higher lows)'

    signal = 'Neutral'
    confidence = 'Medium'

    if latest_rsi > 80:
        signal = 'Extremely Overbought (Strong Bearish)'
        confidence = 'High'
        justification = f'The RSI of {latest_rsi:.1f} is extremely high, indicating strong overbought conditions and high probability of price correction.'
    elif latest_rsi > 70:
        signal = 'Overbought (Bearish)'
        confidence = 'Medium'
        justification = f'The RSI of {latest_rsi:.1f} is above 70, indicating overbought conditions and potential for price pullback.'
    elif latest_rsi < 20:
        signal = 'Extremely Oversold (Strong Bullish)'
        confidence = 'High'
        justification = f'The RSI of {latest_rsi:.1f} is extremely low, indicating strong oversold conditions and high probability of price bounce.'
    elif latest_rsi < 30:
        signal = 'Oversold (Bullish)'
        confidence = 'Medium'
        justification = f'The RSI of {latest_rsi:.1f} is below 30, indicating oversold conditions and potential for price rebound.'
    else:
        justification = f'The RSI is at {latest_rsi:.1f}, which is in the neutral zone (30-70). This suggests balanced buying and selling pressure.'

    if divergence_signal:
        justification += (
            f' Important: {divergence_signal}, which may signal a trend reversal.'
        )
        if 'Bearish Divergence' in divergence_signal and signal in [
            'Overbought (Bearish)',
            'Extremely Overbought (Strong Bearish)',
        ]:
            confidence = 'High'
        elif 'Bullish Divergence' in divergence_signal and signal in [
            'Oversold (Bullish)',
            'Extremely Oversold (Strong Bullish)',
        ]:
            confidence = 'High'

    return {
        'tool': 'RSI',
        'description': 'This tool analyzes the stock data for RSI signals using TA-Lib.',
        'signal': signal,
        'confidence': confidence,
        'justification': justification,
        'details': {
            'RSI_value': round(latest_rsi, 2),
            'strength': f'{round(abs(latest_rsi - 50) * 2, 1)}%',
            'divergence': divergence_signal if divergence_signal else 'None detected',
        },
    }
