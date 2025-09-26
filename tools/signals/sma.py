import numpy as np
import pandas as pd
import talib
from agno.tools import tool
from pandas import DataFrame

from tools.utils import get_ticker, logger_hook, validate_data


@tool(
    name='get_sma_crossover_signal',
    description='This tool analyzes the stock data for SMA crossover signals using TA-Lib.',
    tool_hooks=[logger_hook],
)
def get_sma_crossover_signal(ticker: str):
    df: DataFrame = get_ticker(ticker=ticker)
    short_window = 50
    long_window = 200

    validation_error = validate_data(
        df, ['close', 'high', 'low'], long_window, 'SMA Crossover'
    )
    if validation_error:
        return validation_error

    close_prices = df['close'].values.astype(float)
    high_prices = df['high'].values.astype(float)
    low_prices = df['low'].values.astype(float)

    sma_short = talib.SMA(close_prices, timeperiod=short_window)
    sma_long = talib.SMA(close_prices, timeperiod=long_window)
    atr_values = talib.ATR(high_prices, low_prices, close_prices, timeperiod=14)

    valid_idx = ~(np.isnan(sma_short) | np.isnan(sma_long))
    if np.sum(valid_idx) < 2:
        return {
            'tool': 'SMA Crossover',
            'description': 'This tool analyzes the stock data for SMA crossover signals using TA-Lib.',
            'signal': 'Insufficient Data',
            'justification': 'Not enough valid SMA data points',
            'details': {},
        }

    curr_short = sma_short[-1]
    curr_long = sma_long[-1]
    prev_short = sma_short[-2]
    prev_long = sma_long[-2]
    current_atr = atr_values[-1]
    current_close = close_prices[-1]

    signal = 'Neutral'
    justification = f'The {short_window}-day SMA ({curr_short:.2f}) is currently {"above" if curr_short > curr_long else "below"} the {long_window}-day SMA ({curr_long:.2f}), indicating no recent crossover event.'

    if prev_short < prev_long and curr_short > curr_long:
        signal = 'Golden Cross (Bullish)'
        justification = f'The {short_window}-day SMA just crossed above the {long_window}-day SMA. This is a classic long-term bullish signal, suggesting a potential major uptrend.'
    elif prev_short > prev_long and curr_short < curr_long:
        signal = 'Death Cross (Bearish)'
        justification = f'The {short_window}-day SMA just crossed below the {long_window}-day SMA. This is a classic long-term bearish signal, suggesting a potential major downtrend.'

    volatility_level = 'Normal'
    if current_atr > current_close * 0.03:
        volatility_level = 'High'
    elif current_atr < current_close * 0.01:
        volatility_level = 'Low'

    return {
        'tool': 'SMA Crossover',
        'description': 'This tool analyzes the stock data for SMA crossover signals using TA-Lib.',
        'signal': signal,
        'justification': justification,
        'details': {
            f'SMA_{short_window}': round(curr_short, 2),
            f'SMA_{long_window}': round(curr_long, 2),
            'volatility_during_event': f'{volatility_level} (ATR: {round(current_atr, 2)})',
        },
    }
