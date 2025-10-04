from typing import Any

import numpy as np
import pandas as pd
import talib
import yfinance as yf
from agno.tools import tool
from pandas import DataFrame

from tools.helper import get_ticker, logger_hook, validate_data


@tool(
    name='get_vix_market_fear_signal',
    description='This tool analyzes VIX data for market sentiment signals.',
    tool_hooks=[logger_hook],
)
def get_vix_market_fear_signal() -> dict[str, Any]:
    """
    Analyze VIX (Volatility Index) market fear gauge.

    Returns:
        dict with VIX analysis including tool name, fear signal level,
        justification, and volatility metrics
    """
    try:
        try:
            vix_df = get_ticker('^VIX')
        except Exception:
            vix = yf.Ticker('^VIX')
            vix_df = vix.history(period='1y')
            vix_df.columns = vix_df.columns.str.lower()

        if 'close' not in vix_df.columns or len(vix_df) < 6:
            return {
                'tool': 'VIX (Market Fear Gauge)',
                'description': 'This tool analyzes VIX data for market sentiment signals.',
                'signal': 'Insufficient Data',
                'justification': 'Requires at least 6 data points for the VIX.',
                'details': {},
            }

    except Exception as e:
        return {
            'tool': 'VIX (Market Fear Gauge)',
            'description': 'This tool analyzes VIX data for market sentiment signals.',
            'signal': 'Data Fetch Error',
            'justification': f'Could not fetch VIX data: {e}',
            'details': {},
        }

    latest_vix = vix_df['close'].iloc[-1]

    if latest_vix < 12:
        signal = 'Extremely Low Fear (Complacency Risk)'
        justification = f'VIX at {latest_vix:.1f} indicates extreme complacency. Such low volatility often precedes market corrections.'
    elif latest_vix < 20:
        signal = 'Low Fear (Bullish Environment)'
        justification = f'VIX at {latest_vix:.1f} suggests low volatility and investor confidence. Generally positive for markets.'
    elif latest_vix < 30:
        signal = 'Moderate Fear (Cautious Sentiment)'
        justification = f'VIX at {latest_vix:.1f} indicates elevated uncertainty but not panic levels. Markets may be choppy.'
    elif latest_vix < 40:
        signal = 'High Fear (Risk-Off Mode)'
        justification = f'VIX at {latest_vix:.1f} signals significant fear and uncertainty. Often coincides with market declines.'
    else:
        signal = 'Extreme Fear (Panic Mode)'
        justification = f'VIX at {latest_vix:.1f} indicates extreme fear and panic selling. May present contrarian opportunity.'

    roc_5d = vix_df['close'].pct_change(periods=5).iloc[-1] * 100
    roc_20d = vix_df['close'].pct_change(periods=20).iloc[-1] * 100

    volatility_of_fear = 'Stable'
    if roc_5d > 50:
        volatility_of_fear = 'Spiking Rapidly'
    elif roc_5d > 20:
        volatility_of_fear = 'Increasing'
    elif roc_5d < -30:
        volatility_of_fear = 'Declining Rapidly'
    elif roc_5d < -15:
        volatility_of_fear = 'Decreasing'

    return {
        'tool': 'VIX (Market Fear Gauge)',
        'description': 'This tool analyzes VIX data for market sentiment signals.',
        'signal': signal,
        'justification': justification,
        'details': {
            'vix_level': round(latest_vix, 2),
            'volatility_of_fear': volatility_of_fear,
            'rate_of_change_5d_%': round(roc_5d, 2),
            'rate_of_change_20d_%': round(roc_20d, 2),
        },
    }
