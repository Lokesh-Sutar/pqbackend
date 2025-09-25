import numpy as np
import pandas as pd
import talib
from agno.tools import tool
from pandas import DataFrame

from tools.signals.utils import get_ticker, logger_hook, validate_data


@tool(
    name='get_rsi_signal',  # Fixed: Changed from duplicate name
    description='This tool analyzes the stock data for RSI signals using TA-Lib.',
    tool_hooks=[logger_hook],
)
def get_rsi_signal(ticker: str):
    df: DataFrame = get_ticker(ticker=ticker)

    period = 14

    # Validate data
    validation_error = validate_data(df, ['close'], period + 1, 'RSI')
    if validation_error:
        return validation_error

    # Calculate RSI using TA-Lib (more accurate than manual calculation)
    close_prices = df['close'].values.astype(float)
    rsi_values = talib.RSI(close_prices, timeperiod=period)

    latest_rsi = rsi_values[-1]

    if np.isnan(latest_rsi):
        return {
            'tool': 'RSI',
            'signal': 'Insufficient Data',
            'justification': 'Not enough data to calculate RSI',
            'details': {},
        }

    # Determine signal with more nuanced thresholds
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

    return {
        'tool': 'RSI',
        'signal': signal,
        'confidence': confidence,
        'justification': justification,
        'details': {
            'RSI_value': round(latest_rsi, 2),
            'strength': f'{round(abs(latest_rsi - 50) * 2, 1)}%',
        },
    }
