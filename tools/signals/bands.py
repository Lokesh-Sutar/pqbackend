import numpy as np
import pandas as pd
import talib
from agno.tools import tool
from pandas import DataFrame

from tools.signals.utils import get_ticker, logger_hook, validate_data


@tool(
    name='get_bollinger_bands_signal',
    description='This tool analyzes the stock data for Bollinger Bands signals using TA-Lib.',
    tool_hooks=[logger_hook],
)
def get_bollinger_bands_signal(ticker: str):
    df: DataFrame = get_ticker(ticker=ticker)

    period = 20
    std_devs = 2

    # Validate data
    validation_error = validate_data(df, ['close'], period, 'Bollinger Bands')
    if validation_error:
        return validation_error

    # Calculate Bollinger Bands using TA-Lib
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
            'signal': 'Insufficient Data',
            'justification': 'Not enough data to calculate Bollinger Bands',
            'details': {},
        }

    # Calculate bandwidth
    bandwidth = ((latest_upper - latest_lower) / latest_middle) * 100

    # Calculate %B (position within bands)
    percent_b = (latest_close - latest_lower) / (latest_upper - latest_lower) * 100

    # Volatility analysis
    # Compare current bandwidth to recent average
    recent_bandwidth = (upper_band[-20:] - lower_band[-20:]) / middle_band[-20:] * 100
    avg_bandwidth = np.nanmean(recent_bandwidth)

    if bandwidth < avg_bandwidth * 0.75:
        volatility_signal = 'Squeeze (Low Volatility)'
        volatility_justification = f'Bands are contracting (bandwidth: {bandwidth:.2f}% vs avg: {avg_bandwidth:.2f}%). This often precedes significant price movements.'
    elif bandwidth > avg_bandwidth * 1.25:
        volatility_signal = 'Expansion (High Volatility)'
        volatility_justification = f'Bands are expanding (bandwidth: {bandwidth:.2f}% vs avg: {avg_bandwidth:.2f}%), indicating active trend or high volatility period.'
    else:
        volatility_signal = 'Normal Volatility'
        volatility_justification = f'Bandwidth ({bandwidth:.2f}%) is near normal levels.'

    # Price position analysis
    if percent_b > 100:
        price_position = 'Above Upper Band (Extreme Overbought)'
        price_justification = f'Price is {(percent_b - 100):.1f}% above the upper band. This suggests extreme overbought conditions.'
    elif percent_b > 80:
        price_position = 'Near Upper Band (Overbought)'
        price_justification = f'Price is at {percent_b:.1f}% of the band range, approaching overbought territory.'
    elif percent_b < 0:
        price_position = 'Below Lower Band (Extreme Oversold)'
        price_justification = f'Price is {abs(percent_b):.1f}% below the lower band. This suggests extreme oversold conditions.'
    elif percent_b < 20:
        price_position = 'Near Lower Band (Oversold)'
        price_justification = f'Price is at {percent_b:.1f}% of the band range, approaching oversold territory.'
    else:
        price_position = 'Mid-Range'
        price_justification = f'Price is at {percent_b:.1f}% of the band range, indicating normal trading conditions.'

    return {
        'tool': 'Bollinger Bands',
        'volatility_signal': volatility_signal,
        'volatility_justification': volatility_justification,
        'price_position': price_position,
        'price_justification': price_justification,
        'details': {
            'Upper_Band': round(latest_upper, 2),
            'Middle_Band': round(latest_middle, 2),
            'Lower_Band': round(latest_lower, 2),
            'Bandwidth_%': round(bandwidth, 2),
            'Percent_B': round(percent_b, 1),
            'Current_Price': round(latest_close, 2),
        },
    }
