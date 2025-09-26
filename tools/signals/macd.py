import numpy as np
import pandas as pd
import talib
from agno.tools import tool
from pandas import DataFrame

from tools.utils import get_ticker, logger_hook, validate_data


@tool(
    name='get_macd_signal',
    description='This tool analyzes the stock data for MACD signals using TA-Lib.',
    tool_hooks=[logger_hook],
)
def get_macd_signal(ticker: str):
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

    if any(np.isnan([curr_macd, curr_signal, prev_macd, prev_signal])):
        return {
            'tool': 'MACD',
            'description': 'This tool analyzes the stock data for MACD signals using TA-Lib.',
            'signal': 'Insufficient Data',
            'justification': 'Not enough data to calculate MACD',
            'details': {},
        }

    signal = 'Neutral'
    momentum_direction = 'bullish' if curr_macd > curr_signal else 'bearish'

    if prev_macd <= prev_signal and curr_macd > curr_signal:
        signal = 'Bullish Crossover'
        justification = 'The MACD line has just crossed above its signal line. This bullish crossover suggests upward momentum is accelerating.'
    elif prev_macd >= prev_signal and curr_macd < curr_signal:
        signal = 'Bearish Crossover'
        justification = 'The MACD line has just crossed below its signal line. This bearish crossover suggests downward momentum is accelerating.'
    else:
        justification = f'The MACD line ({curr_macd:.4f}) is currently {"above" if curr_macd > curr_signal else "below"} its signal line ({curr_signal:.4f}), indicating {momentum_direction} momentum but no recent crossover.'

    histogram_trend = (
        'strengthening' if abs(curr_histogram) > abs(histogram[-2]) else 'weakening'
    )

    return {
        'tool': 'MACD',
        'description': 'This tool analyzes the stock data for MACD signals using TA-Lib.',
        'signal': signal,
        'justification': justification + f' The histogram is {histogram_trend}.',
        'details': {
            'MACD_line': round(curr_macd, 4),
            'Signal_line': round(curr_signal, 4),
            'Histogram': round(curr_histogram, 4),
            'momentum_direction': momentum_direction,
        },
    }
