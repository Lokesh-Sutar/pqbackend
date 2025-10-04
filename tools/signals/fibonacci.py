from typing import Any

import numpy as np
import talib
from agno.tools import tool
from pandas import DataFrame

from tools.helper import get_ticker, logger_hook, validate_data

# Try to import scipy, but provide fallback if not available
try:
    from scipy.signal import argrelextrema

    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


@tool(
    name='get_fibonacci_retracement',
    description='This tool calculates Fibonacci Retracement levels based on recent price swings.',
    tool_hooks=[logger_hook],
)
def get_fibonacci_retracement(ticker: str) -> dict[str, Any]:
    """
    Calculate Fibonacci Retracement levels based on the last significant price swing.

    Args:
        ticker: Stock ticker symbol (e.g., 'NVDA', 'AAPL')

    Returns:
        dict with Fibonacci levels including tool name, trend direction,
        key support/resistance levels, and justification
    """
    df: DataFrame = get_ticker(ticker=ticker)

    period = 63

    validation_error = validate_data(
        df, ['high', 'low', 'close'], period, 'Fibonacci Retracement'
    )
    if validation_error:
        return validation_error

    try:
        period_df = df.iloc[-period:].copy()

        high_values = period_df['high'].values
        low_values = period_df['low'].values

        if SCIPY_AVAILABLE:
            local_max_indices = argrelextrema(high_values, np.greater, order=5)[0]
            local_min_indices = argrelextrema(low_values, np.less, order=5)[0]

            if len(local_max_indices) > 0 and len(local_min_indices) > 0:
                price_max = float(high_values[local_max_indices[-1]])
                price_min = float(low_values[local_min_indices[-1]])
            else:
                price_max = float(period_df['high'].max())
                price_min = float(period_df['low'].min())
        else:
            price_max = float(period_df['high'].max())
            price_min = float(period_df['low'].min())

        price_range = price_max - price_min

        close_prices = df['close'].values.astype(float)
        current_price = float(close_prices[-1])

        sma_20 = talib.SMA(close_prices, timeperiod=20)
        sma_50 = talib.SMA(close_prices, timeperiod=50)

        if np.isnan(sma_20[-1]) or np.isnan(sma_50[-1]):
            is_uptrend = current_price > df['close'].iloc[-period]
        else:
            is_uptrend = (current_price > sma_20[-1]) and (sma_20[-1] > sma_50[-1])

        if price_range == 0 or np.isnan(price_range):
            return {
                'tool': 'Fibonacci Retracement',
                'description': 'This tool calculates Fibonacci Retracement levels based on recent price swings.',
                'signal': 'Insufficient Price Movement',
                'justification': f'The price range in the last {period} days is too small to generate meaningful Fibonacci levels.',
                'details': {},
            }

        levels = {}
        justification = ''

        if is_uptrend:
            justification = f'The market is in an uptrend (current: ${current_price:.2f}). These levels represent commonly-watched support zones where traders may look for pullback entries. Price MAY find support at these levels.'
            levels['23.6%'] = round(price_max - (price_range * 0.236), 2)
            levels['38.2%'] = round(price_max - (price_range * 0.382), 2)
            levels['50.0%'] = round(price_max - (price_range * 0.5), 2)
            levels['61.8%'] = round(price_max - (price_range * 0.618), 2)
        else:
            justification = f'The market is in a downtrend (current: ${current_price:.2f}). These levels represent commonly-watched resistance zones where traders may look for rally entries. Price MAY find resistance at these levels.'
            levels['23.6%'] = round(price_min + (price_range * 0.236), 2)
            levels['38.2%'] = round(price_min + (price_range * 0.382), 2)
            levels['50.0%'] = round(price_min + (price_range * 0.5), 2)
            levels['61.8%'] = round(price_min + (price_range * 0.618), 2)

        return {
            'tool': 'Fibonacci Retracement',
            'description': 'This tool calculates Fibonacci Retracement levels based on recent price swings.',
            'signal': 'Uptrend' if is_uptrend else 'Downtrend',
            'justification': justification,
            'details': {
                'Current_Price': round(current_price, 2),
                'Swing_High': round(price_max, 2),
                'Swing_Low': round(price_min, 2),
                'Price_Range': round(price_range, 2),
                'Fib_Levels': levels,
            },
        }

    except Exception as e:
        return {
            'tool': 'Fibonacci Retracement',
            'description': 'This tool calculates Fibonacci Retracement levels based on recent price swings.',
            'signal': 'Calculation Error',
            'justification': f'Error calculating Fibonacci levels: {str(e)}',
            'details': {},
        }
