from typing import Any

import numpy as np
import pandas as pd
import talib
from agno.tools import tool
from pandas import DataFrame

from tools.helper import get_ticker, logger_hook, validate_data


@tool(
    name='get_macd_signal',
    description='This tool analyzes the stock data for MACD signals using TA-Lib.',
    tool_hooks=[logger_hook],
)
def get_macd_signal(ticker: str) -> dict[str, Any]:
    """
    Analyze MACD (Moving Average Convergence Divergence) for a stock ticker.

    Args:
        ticker: Stock ticker symbol (e.g., 'NVDA', 'AAPL')

    Returns:
        dict with MACD analysis including tool name, signal type (Bullish/Bearish Crossover or Neutral),
        justification, and MACD line details
    """
    df: DataFrame = get_ticker(ticker=ticker)

    fast = 12
    slow = 26
    signal_period = 9

    validation_error = validate_data(df, ['close'], slow + signal_period, 'MACD')
    if validation_error:
        return validation_error

    close_prices = df['close'].values.astype(float)
    macd_line, signal_line, histogram = talib.MACD(
        close_prices, fastperiod=fast, slowperiod=slow, signalperiod=signal_period
    )

    curr_macd = macd_line[-1]
    curr_signal = signal_line[-1]
    curr_histogram = histogram[-1]
    prev_macd = macd_line[-2]
    prev_signal = signal_line[-2]
    prev_histogram = histogram[-2]

    if any(np.isnan([curr_macd, curr_signal, prev_macd, prev_signal])):
        return {
            'tool': 'MACD',
            'description': 'This tool analyzes the stock data for MACD signals using TA-Lib.',
            'signal': 'Insufficient Data',
            'justification': 'Not enough data to calculate MACD',
            'details': {},
        }

    zero_line_cross = None
    if len(macd_line) >= 2:
        if prev_macd <= 0 and curr_macd > 0:
            zero_line_cross = 'Bullish (Crossed Above Zero)'
        elif prev_macd >= 0 and curr_macd < 0:
            zero_line_cross = 'Bearish (Crossed Below Zero)'

    divergence_signal = None
    if len(close_prices) >= 20 and len(macd_line) >= 20:
        recent_prices = close_prices[-20:]
        recent_macd = macd_line[-20:]

        price_trend = np.polyfit(range(len(recent_prices)), recent_prices, 1)[0]
        macd_trend = np.polyfit(range(len(recent_macd)), recent_macd, 1)[0]

        if price_trend > 0 and macd_trend < 0:
            divergence_signal = 'Bearish Divergence (Warning)'
        elif price_trend < 0 and macd_trend > 0:
            divergence_signal = 'Bullish Divergence (Reversal Signal)'

    signal = 'Neutral'
    momentum_direction = 'bullish' if curr_macd > curr_signal else 'bearish'
    confidence = 'Medium'

    if prev_macd <= prev_signal and curr_macd > curr_signal:
        signal = 'Bullish Crossover'
        confidence = (
            'High' if zero_line_cross == 'Bullish (Crossed Above Zero)' else 'Medium'
        )
        justification = 'The MACD line has just crossed above its signal line. This bullish crossover suggests upward momentum is accelerating.'
        if zero_line_cross:
            justification += ' Additionally, MACD crossed above the zero line, confirming bullish momentum.'
    elif prev_macd >= prev_signal and curr_macd < curr_signal:
        signal = 'Bearish Crossover'
        confidence = (
            'High' if zero_line_cross == 'Bearish (Crossed Below Zero)' else 'Medium'
        )
        justification = 'The MACD line has just crossed below its signal line. This bearish crossover suggests downward momentum is accelerating.'
        if zero_line_cross:
            justification += ' Additionally, MACD crossed below the zero line, confirming bearish momentum.'
    else:
        justification = f'The MACD line ({curr_macd:.4f}) is currently {"above" if curr_macd > curr_signal else "below"} its signal line ({curr_signal:.4f}), indicating {momentum_direction} momentum but no recent crossover.'

        if zero_line_cross:
            signal = zero_line_cross.split(' ')[0]
            justification += (
                f' {zero_line_cross}, which adds to the {momentum_direction} case.'
            )
            confidence = 'Medium'

    histogram_trend = (
        'strengthening' if abs(curr_histogram) > abs(prev_histogram) else 'weakening'
    )

    if divergence_signal:
        justification += f' Note: {divergence_signal} detected over the last 20 periods.'

    return {
        'tool': 'MACD',
        'description': 'This tool analyzes the stock data for MACD signals using TA-Lib.',
        'signal': signal,
        'confidence': confidence,
        'justification': justification + f' The histogram is {histogram_trend}.',
        'details': {
            'MACD_line': round(curr_macd, 4),
            'Signal_line': round(curr_signal, 4),
            'Histogram': round(curr_histogram, 4),
            'momentum_direction': momentum_direction,
            'zero_line_position': 'Above' if curr_macd > 0 else 'Below',
            'divergence': divergence_signal if divergence_signal else 'None detected',
        },
    }
