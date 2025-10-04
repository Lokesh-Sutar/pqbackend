from typing import Any

import numpy as np
import pandas as pd
import talib
from agno.tools import tool
from pandas import DataFrame

from tools.helper import get_ticker, logger_hook, validate_data


@tool(
    name='get_bollinger_bands_signal',
    description='This tool analyzes the stock data for Bollinger Bands signals using TA-Lib.',
    tool_hooks=[logger_hook],
)
def get_bollinger_bands_signal(ticker: str) -> dict[str, Any]:
    """
    Analyze Bollinger Bands for a stock ticker.

    Args:
        ticker: Stock ticker symbol (e.g., 'NVDA', 'AAPL')

    Returns:
        dict with Bollinger Bands analysis including tool name, signal type,
        volatility signals, price position, and band details
    """
    df: DataFrame = get_ticker(ticker=ticker)

    period = 20
    std_devs = 2

    validation_error = validate_data(df, ['close'], period, 'Bollinger Bands')
    if validation_error:
        return validation_error

    close_prices = df['close'].values.astype(float)
    upper_band, middle_band, lower_band = talib.BBANDS(
        close_prices, timeperiod=period, nbdevup=std_devs, nbdevdn=std_devs
    )

    latest_close = close_prices[-1]
    latest_upper = upper_band[-1]
    latest_middle = middle_band[-1]
    latest_lower = lower_band[-1]

    if any(np.isnan([latest_upper, latest_middle, latest_lower])):
        return {
            'tool': 'Bollinger Bands',
            'description': 'This tool analyzes the stock data for Bollinger Bands signals using TA-Lib.',
            'signal': 'Insufficient Data',
            'justification': 'Not enough data to calculate Bollinger Bands',
            'details': {},
        }

    bandwidth = ((latest_upper - latest_lower) / latest_middle) * 100

    percent_b = (latest_close - latest_lower) / (latest_upper - latest_lower) * 100

    recent_bandwidth = (upper_band[-20:] - lower_band[-20:]) / middle_band[-20:] * 100
    avg_bandwidth = np.nanmean(recent_bandwidth)

    band_walk = None
    if len(close_prices) >= 5:
        recent_closes = close_prices[-5:]
        recent_upper = upper_band[-5:]
        recent_lower = lower_band[-5:]

        upper_proximity = np.mean(
            [
                (upper - closes) / (upper - lower)
                for closes, upper, lower in zip(recent_closes, recent_upper, recent_lower)
            ]
        )

        if upper_proximity < 0.15:
            band_walk = 'Walking Upper Band (Strong Uptrend)'
        elif upper_proximity > 0.85:
            band_walk = 'Walking Lower Band (Strong Downtrend)'

    if bandwidth < avg_bandwidth * 0.75:
        volatility_signal = 'Squeeze (Low Volatility)'
        volatility_justification = f'Bands are contracting (bandwidth: {bandwidth:.2f}% vs avg: {avg_bandwidth:.2f}%). This often precedes significant price movements.'
    elif bandwidth > avg_bandwidth * 1.25:
        volatility_signal = 'Expansion (High Volatility)'
        volatility_justification = f'Bands are expanding (bandwidth: {bandwidth:.2f}% vs avg: {avg_bandwidth:.2f}%), indicating active trend or high volatility period.'
    else:
        volatility_signal = 'Normal Volatility'
        volatility_justification = f'Bandwidth ({bandwidth:.2f}%) is near normal levels.'

    if percent_b > 100:
        price_position = 'Above Upper Band (Extreme Overbought)'
        price_justification = f'Price is {(percent_b - 100):.1f}% above the upper band. This suggests extreme overbought conditions.'
        if band_walk == 'Walking Upper Band (Strong Uptrend)':
            price_justification += ' However, persistent band walking indicates a strong uptrend may continue.'
    elif percent_b > 80:
        price_position = 'Near Upper Band (Overbought)'
        price_justification = f'Price is at {percent_b:.1f}% of the band range, approaching overbought territory.'
        if band_walk == 'Walking Upper Band (Strong Uptrend)':
            price_justification += (
                ' Band walking suggests this could be part of a strong trending move.'
            )
    elif percent_b < 0:
        price_position = 'Below Lower Band (Extreme Oversold)'
        price_justification = f'Price is {abs(percent_b):.1f}% below the lower band. This suggests extreme oversold conditions.'
        if band_walk == 'Walking Lower Band (Strong Downtrend)':
            price_justification += ' However, persistent band walking indicates a strong downtrend may continue.'
    elif percent_b < 20:
        price_position = 'Near Lower Band (Oversold)'
        price_justification = f'Price is at {percent_b:.1f}% of the band range, approaching oversold territory.'
        if band_walk == 'Walking Lower Band (Strong Downtrend)':
            price_justification += (
                ' Band walking suggests this could be part of a strong trending move.'
            )
    else:
        price_position = 'Mid-Range'
        price_justification = f'Price is at {percent_b:.1f}% of the band range, indicating normal trading conditions.'

    return {
        'tool': 'Bollinger Bands',
        'description': 'This tool analyzes the stock data for Bollinger Bands signals using TA-Lib.',
        'signal': f'{volatility_signal} | {price_position}',
        'justification': f'{volatility_justification} {price_justification}',
        'volatility_signal': volatility_signal,
        'price_position': price_position,
        'details': {
            'Upper_Band': round(latest_upper, 2),
            'Middle_Band': round(latest_middle, 2),
            'Lower_Band': round(latest_lower, 2),
            'Bandwidth_%': round(bandwidth, 2),
            'Percent_B': round(percent_b, 1),
            'Current_Price': round(latest_close, 2),
            'Band_Walk': band_walk if band_walk else 'None',
        },
    }
