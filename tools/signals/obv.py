from typing import Any

import numpy as np
import talib
from agno.tools import tool
from pandas import DataFrame

from tools.helper import get_ticker, logger_hook, validate_data


@tool(
    name='get_obv_signal',
    description='This tool analyzes the stock data for On-Balance Volume (OBV) signals using TA-Lib.',
    tool_hooks=[logger_hook],
)
def get_obv_signal(ticker: str) -> dict[str, Any]:
    """
    Analyze On-Balance Volume (OBV) to gauge trend strength and conviction.

    Args:
        ticker: Stock ticker symbol (e.g., 'NVDA', 'AAPL')

    Returns:
        dict with OBV analysis including tool name, signal type (Bullish/Bearish Divergence or Neutral),
        justification, and OBV trend details
    """
    df: DataFrame = get_ticker(ticker=ticker)

    period = 50

    validation_error = validate_data(df, ['close', 'volume'], period, 'OBV')
    if validation_error:
        return validation_error

    try:
        close_prices = df['close'].values.astype(float)
        volume = df['volume'].values.astype(float)

        obv = talib.OBV(close_prices, volume)

        if np.isnan(obv[-1]):
            return {
                'tool': 'OBV',
                'description': 'This tool analyzes the stock data for On-Balance Volume (OBV) signals using TA-Lib.',
                'signal': 'Insufficient Data',
                'justification': 'Not enough data to calculate OBV',
                'details': {},
            }

        price_recent = close_prices[-period:]
        obv_recent = obv[-period:]

        if np.any(np.isnan(price_recent)) or np.any(np.isnan(obv_recent)):
            return {
                'tool': 'OBV',
                'description': 'This tool analyzes the stock data for On-Balance Volume (OBV) signals using TA-Lib.',
                'signal': 'Insufficient Data',
                'justification': 'Data contains NaN values in recent period',
                'details': {},
            }

        price_trend_slope = np.polyfit(range(len(price_recent)), price_recent, 1)[0]
        obv_trend_slope = np.polyfit(range(len(obv_recent)), obv_recent, 1)[0]

        price_slope_pct = (
            (price_trend_slope / price_recent[0]) * 100 if price_recent[0] != 0 else 0
        )
        obv_slope_pct = (
            (obv_trend_slope / abs(obv_recent[0])) * 100 if obv_recent[0] != 0 else 0
        )

        divergence_strength = abs(price_slope_pct) + abs(obv_slope_pct)

        is_significant = divergence_strength > 0.1

        signal = 'Neutral'
        justification = 'The price and On-Balance Volume (OBV) are moving in the same direction, confirming the current trend. This suggests buying/selling pressure aligns with price movement.'
        confidence = 'Medium'

        if price_trend_slope > 0 and obv_trend_slope <= 0:
            if is_significant:
                signal = 'Bearish Divergence (Strong Warning)'
                confidence = 'High'
                justification = f'The stock price is rising but OBV is declining or flat over {period} days. This significant divergence suggests a lack of volume support and warns that the uptrend may be weak and could reverse. Divergence strength: {divergence_strength:.2f}'
            else:
                signal = 'Bearish Divergence (Weak Warning)'
                confidence = 'Low'
                justification = f'The stock price is slightly rising while OBV is flat or declining, but the divergence is weak. Monitor for strengthening divergence. Divergence strength: {divergence_strength:.2f}'

        elif price_trend_slope < 0 and obv_trend_slope >= 0:
            if is_significant:
                signal = 'Bullish Divergence (Strong Reversal Signal)'
                confidence = 'High'
                justification = f'The stock price is falling but OBV is rising or flat over {period} days. This significant divergence indicates accumulation is occurring despite the price drop, suggesting the downtrend could reverse. Divergence strength: {divergence_strength:.2f}'
            else:
                signal = 'Bullish Divergence (Weak Reversal Signal)'
                confidence = 'Low'
                justification = f'The stock price is slightly falling while OBV is flat or rising, but the divergence is weak. Monitor for strengthening divergence. Divergence strength: {divergence_strength:.2f}'

        return {
            'tool': 'OBV',
            'description': 'This tool analyzes the stock data for On-Balance Volume (OBV) signals using TA-Lib.',
            'signal': signal,
            'confidence': confidence,
            'justification': justification,
            'details': {
                'Current_OBV': round(obv[-1], 0),
                'Price_Trend_50d': 'Up' if price_trend_slope > 0 else 'Down',
                'OBV_Trend_50d': 'Up' if obv_trend_slope > 0 else 'Down',
                'Price_Slope_%_per_day': round(price_slope_pct, 4),
                'OBV_Slope_%_per_day': round(obv_slope_pct, 4),
                'Divergence_Strength': round(divergence_strength, 4),
            },
        }

    except Exception as e:
        return {
            'tool': 'OBV',
            'description': 'This tool analyzes the stock data for On-Balance Volume (OBV) signals using TA-Lib.',
            'signal': 'Calculation Error',
            'justification': f'Error calculating OBV signal: {str(e)}',
            'details': {},
        }
