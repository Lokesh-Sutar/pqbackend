from typing import Any

import numpy as np
import talib
from agno.tools import tool
from pandas import DataFrame

from tools.helper import get_ticker, logger_hook, validate_data


@tool(
    name='get_ichimoku_cloud_signal',
    description='This tool analyzes the stock data for Ichimoku Cloud signals.',
    tool_hooks=[logger_hook],
)
def get_ichimoku_cloud_signal(ticker: str) -> dict[str, Any]:
    """
    Analyze the Ichimoku Cloud for comprehensive trend and momentum signals.

    Args:
        ticker: Stock ticker symbol (e.g., 'NVDA', 'AAPL')

    Returns:
        dict with Ichimoku Cloud analysis including tool name, signal type,
        cloud position, and trend strength
    """
    df: DataFrame = get_ticker(ticker=ticker)

    min_periods = 52 + 26

    validation_error = validate_data(
        df, ['high', 'low', 'close'], min_periods, 'Ichimoku Cloud'
    )
    if validation_error:
        return validation_error

    high_prices = df['high'].values.astype(float)
    low_prices = df['low'].values.astype(float)
    close_prices = df['close'].values.astype(float)

    nine_high = talib.MAX(high_prices, timeperiod=9)
    nine_low = talib.MIN(low_prices, timeperiod=9)
    tenkan_sen = (nine_high + nine_low) / 2

    twenty_six_high = talib.MAX(high_prices, timeperiod=26)
    twenty_six_low = talib.MIN(low_prices, timeperiod=26)
    kijun_sen = (twenty_six_high + twenty_six_low) / 2

    senkou_span_a = (tenkan_sen + kijun_sen) / 2

    fifty_two_high = talib.MAX(high_prices, timeperiod=52)
    fifty_two_low = talib.MIN(low_prices, timeperiod=52)
    senkou_span_b = (fifty_two_high + fifty_two_low) / 2

    latest_close = close_prices[-1]

    current_span_a = senkou_span_a[-1]
    current_span_b = senkou_span_b[-1]
    current_tenkan = tenkan_sen[-1]
    current_kijun = kijun_sen[-1]

    if any(
        np.isnan(
            [
                current_span_a,
                current_span_b,
                current_tenkan,
                current_kijun,
                latest_close,
            ]
        )
    ):
        return {
            'tool': 'Ichimoku Cloud',
            'description': 'This tool analyzes the stock data for Ichimoku Cloud signals.',
            'signal': 'Insufficient Data',
            'justification': 'Not enough data to calculate Ichimoku Cloud components',
            'details': {},
        }

    cloud_top = max(current_span_a, current_span_b)
    cloud_bottom = min(current_span_a, current_span_b)
    cloud_thickness = cloud_top - cloud_bottom

    tk_cross_bullish = current_tenkan > current_kijun

    signal = 'Neutral / In Cloud'
    justification = f'The price (${latest_close:.2f}) is currently trading inside the Ichimoku Cloud (${cloud_bottom:.2f} - ${cloud_top:.2f}), indicating a period of indecision or consolidation. The trend is unclear.'

    if latest_close > cloud_top:
        distance_pct = ((latest_close - cloud_top) / cloud_top) * 100

        if distance_pct > 5 and tk_cross_bullish:
            signal = 'Very Strong Bullish'
            justification = f'The price (${latest_close:.2f}) is trading {distance_pct:.1f}% above the Ichimoku Cloud (${cloud_top:.2f}), with Tenkan-sen above Kijun-sen. This is a very strong bullish signal. The cloud is expected to act as a support zone.'
        elif distance_pct > 2:
            signal = 'Strong Bullish'
            justification = f'The price (${latest_close:.2f}) is trading {distance_pct:.1f}% above the Ichimoku Cloud (${cloud_top:.2f}), which is a strong bullish signal. The cloud is expected to act as a support zone.'
        else:
            signal = 'Bullish'
            justification = f'The price (${latest_close:.2f}) has just moved above the Ichimoku Cloud (${cloud_top:.2f}). This is a bullish signal, though proximity to the cloud suggests caution.'

    elif latest_close < cloud_bottom:
        distance_pct = ((cloud_bottom - latest_close) / cloud_bottom) * 100

        if distance_pct > 5 and not tk_cross_bullish:
            signal = 'Very Strong Bearish'
            justification = f'The price (${latest_close:.2f}) is trading {distance_pct:.1f}% below the Ichimoku Cloud (${cloud_bottom:.2f}), with Tenkan-sen below Kijun-sen. This is a very strong bearish signal. The cloud is expected to act as a resistance zone.'
        elif distance_pct > 2:
            signal = 'Strong Bearish'
            justification = f'The price (${latest_close:.2f}) is trading {distance_pct:.1f}% below the Ichimoku Cloud (${cloud_bottom:.2f}), which is a strong bearish signal. The cloud is expected to act as a resistance zone.'
        else:
            signal = 'Bearish'
            justification = f'The price (${latest_close:.2f}) has just moved below the Ichimoku Cloud (${cloud_bottom:.2f}). This is a bearish signal, though proximity to the cloud suggests caution.'

    cloud_color = (
        'Bullish (Green)' if current_span_a > current_span_b else 'Bearish (Red)'
    )

    return {
        'tool': 'Ichimoku Cloud',
        'description': 'This tool analyzes the stock data for Ichimoku Cloud signals.',
        'signal': signal,
        'justification': justification,
        'details': {
            'Current_Price': round(latest_close, 2),
            'Cloud_Top': round(cloud_top, 2),
            'Cloud_Bottom': round(cloud_bottom, 2),
            'Cloud_Thickness': round(cloud_thickness, 2),
            'Cloud_Color': cloud_color,
            'Tenkan_Sen': round(current_tenkan, 2),
            'Kijun_Sen': round(current_kijun, 2),
            'TK_Cross': 'Bullish' if tk_cross_bullish else 'Bearish',
        },
    }
