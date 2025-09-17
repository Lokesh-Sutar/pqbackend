import pathlib
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd
import yfinance as yf
from agno.tools import tool
from pandas import DataFrame


def logger_hook(function_name: str, function_call: Callable, arguments: dict[str, Any]):
    """Hook function that wraps the tool execution"""
    print(f'About to call {function_name} with arguments: {arguments}')
    result = function_call(**arguments)
    print(f'Function call completed with result: {result}')
    return result


def get_ticker(ticker: str) -> pd.DataFrame:
    data_dir = Path(__file__).resolve().parent.parent / 'data'
    df_file = data_dir / f'{ticker}.csv'
    df: pd.DataFrame = pd.read_csv(df_file)
    print('TICKER IS LOADED')
    # df = yf.Ticker(ticker)
    return df


@tool(
    name='get_sma_crossover_signal',
    description='This tool analyzes the stock data for SMA crossover signals.',
    tool_hooks=[logger_hook],
)
def get_sma_crossover_signal(ticker: str):
    df: DataFrame = get_ticker(ticker=ticker)

    short_window = 50
    long_window = 200

    if (
        'close' not in df.columns
        or 'high' not in df.columns
        or 'low' not in df.columns
        or len(df) < long_window
    ):
        return {
            'tool': 'SMA Crossover',
            'signal': 'Insufficient Data',
            'justification': f"Requires at least {long_window} data points and 'close', 'high', 'low' columns.",
            'details': {},
        }

    df_copy = df.copy()
    df_copy['SMA_short'] = df_copy['close'].rolling(window=short_window).mean()
    df_copy['SMA_long'] = df_copy['close'].rolling(window=long_window).mean()

    prev_day = df_copy.iloc[-2]
    curr_day = df_copy.iloc[-1]

    signal = 'Neutral'
    justification = f'The {short_window}-day SMA is currently {"above" if curr_day["SMA_short"] > curr_day["SMA_long"] else "below"} the {long_window}-day SMA, indicating no recent crossover event.'

    if (
        prev_day['SMA_short'] < prev_day['SMA_long']
        and curr_day['SMA_short'] > curr_day['SMA_long']
    ):
        signal = 'Golden Cross (Bullish)'
        justification = f'The {short_window}-day SMA just crossed above the {long_window}-day SMA. This is a classic long-term bullish signal, suggesting a potential major uptrend.'

    elif (
        prev_day['SMA_short'] > prev_day['SMA_long']
        and curr_day['SMA_short'] < curr_day['SMA_long']
    ):
        signal = 'Death Cross (Bearish)'
        justification = f'The {short_window}-day SMA just crossed below the {long_window}-day SMA. This is a classic long-term bearish signal, suggesting a potential major downtrend.'

    high_low = df_copy['high'] - df_copy['low']
    high_prev_close = np.abs(df_copy['high'] - df_copy['close'].shift(1))
    low_prev_close = np.abs(df_copy['low'] - df_copy['close'].shift(1))
    true_range = pd.concat(
        [high_low, high_prev_close, low_prev_close],  # type: ignore
        axis=1,  # type: ignore
    ).max(axis=1)  # type: ignore
    atr = true_range.rolling(window=14).mean().iloc[-1]

    volatility_level = 'Normal'
    if atr > df_copy['close'].iloc[-1] * 0.03:
        volatility_level = 'High'

    return {
        'tool': 'SMA Crossover',
        'signal': signal,
        'justification': justification,
        'details': {
            f'SMA_{short_window}': round(curr_day['SMA_short'], 2),
            f'SMA_{long_window}': round(curr_day['SMA_long'], 2),
            'volatility_during_event': f'{volatility_level} (ATR: {round(atr, 2)})',
        },
    }


@tool(
    name='get_sma_crossover_signal',
    description='This tool analyzes the stock data for SMA crossover signals.',
    tool_hooks=[logger_hook],
)
def get_rsi_signal(ticker: str):
    df: DataFrame = get_ticker(ticker=ticker)

    period = 14

    if 'close' not in df.columns or len(df) < period:
        return {
            'tool': 'RSI',
            'signal': 'Insufficient Data',
            'justification': f'Requires at least {period} data points.',
            'details': {},
        }

    df_copy = df.copy()
    delta = df_copy['close'].diff()
    gains = delta.where(delta > 0, 0)  # pyright: ignore[reportOperatorIssue]
    losses = -delta.where(delta < 0, 0)  # pyright: ignore[reportOperatorIssue]

    avg_gain = gains.ewm(alpha=1 / period, adjust=False).mean()
    avg_loss = losses.ewm(alpha=1 / period, adjust=False).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    latest_rsi = rsi.iloc[-1]

    signal = 'Neutral'
    justification = f'The RSI is at {round(latest_rsi, 1)}, which is in the neutral zone. This suggests the stock is neither overbought nor oversold at the moment.'

    if latest_rsi > 70:
        signal = 'Overbought (Bearish)'
        justification = f'The RSI of {round(latest_rsi, 1)} is above 70. This indicates the stock has risen quickly and may be due for a price correction or pullback.'
    elif latest_rsi < 30:
        signal = 'Oversold (Bullish)'
        justification = f'The RSI of {round(latest_rsi, 1)} is below 30. This indicates the stock has fallen quickly and may be due for a rebound.'

    return {
        'tool': 'RSI',
        'signal': signal,
        'justification': justification,
        'details': {
            'RSI_value': round(latest_rsi, 2),
            'confidence': f'{round(abs(latest_rsi - 50) * 2, 1)}%',
        },
    }


@tool(
    name='get_macd_signal',
    description='This tool analyzes the stock data for MACD signals.',
    tool_hooks=[logger_hook],
)
def get_macd_signal(ticker: str):
    df: DataFrame = get_ticker(ticker=ticker)

    fast = 12
    slow = 26
    signal_period = 9

    if 'close' not in df.columns or len(df) < slow:
        return {
            'tool': 'MACD',
            'signal': 'Insufficient Data',
            'justification': f'Requires at least {slow} data points.',
            'details': {},
        }

    df_copy = df.copy()
    ema_fast = df_copy['close'].ewm(span=fast, adjust=False).mean()
    ema_slow = df_copy['close'].ewm(span=slow, adjust=False).mean()

    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()

    prev_macd = macd_line.iloc[-2]
    curr_macd = macd_line.iloc[-1]
    prev_signal = signal_line.iloc[-2]
    curr_signal = signal_line.iloc[-1]

    signal = 'Neutral'
    justification = f'The MACD line is currently {"above" if curr_macd > curr_signal else "below"} its signal line, indicating {"bullish" if curr_macd > curr_signal else "bearish"} momentum but no recent crossover.'

    if prev_macd < prev_signal and curr_macd > curr_signal:
        signal = 'Bullish Crossover'
        justification = 'The MACD line has just crossed above its signal line. This is a bullish signal that suggests upward momentum is accelerating.'
    elif prev_macd > prev_signal and curr_macd < curr_signal:
        signal = 'Bearish Crossover'
        justification = 'The MACD line has just crossed below its signal line. This is a bearish signal that suggests downward momentum is accelerating.'

    return {
        'tool': 'MACD',
        'signal': signal,
        'justification': justification,
        'details': {
            'MACD_line': round(curr_macd, 3),
            'Signal_line': round(curr_signal, 3),
            'Histogram': round(curr_macd - curr_signal, 3),
        },
    }


@tool(
    name='get_bollinger_bands_signal',
    description='This tool analyzes the stock data for Bollinger Bands signals.',
    tool_hooks=[logger_hook],
)
def get_bollinger_bands_signal(ticker: str):
    df: DataFrame = get_ticker(ticker=ticker)

    period = 20
    std_devs = 2

    if 'close' not in df.columns or len(df) < period:
        return {
            'tool': 'Bollinger Bands',
            'signal': 'Insufficient Data',
            'justification': f'Requires at least {period} data points.',
            'details': {},
        }

    df_copy = df.copy()
    sma = df_copy['close'].rolling(window=period).mean()
    std = df_copy['close'].rolling(window=period).std()

    upper_band = sma + (std_devs * std)
    lower_band = sma - (std_devs * std)

    bandwidth = ((upper_band - lower_band) / sma) * 100
    latest_bandwidth = bandwidth.iloc[-1]
    latest_close = df_copy['close'].iloc[-1]
    latest_upper = upper_band.iloc[-1]
    latest_lower = lower_band.iloc[-1]

    volatility_signal = 'Breakout (High Volatility)'
    volatility_justification = f'The Bollinger Bands are relatively wide (bandwidth: {round(latest_bandwidth, 2)}%), indicating a period of high volatility and a strong current trend.'
    if latest_bandwidth < bandwidth.quantile(0.25):
        volatility_signal = 'Squeeze (Low Volatility)'
        volatility_justification = f'The Bollinger Bands are narrow (bandwidth: {round(latest_bandwidth, 2)}%), indicating a period of low volatility. This often precedes a significant price move.'

    price_position = 'Mid-Range'
    price_justification = 'The price is trading between the middle and outer bands.'
    if latest_close > latest_upper:
        price_position = 'Above Upper Band (Overbought)'
        price_justification = 'The price has closed above the upper band, suggesting it is statistically expensive and could be due for a pullback.'
    elif latest_close < latest_lower:
        price_position = 'Below Lower Band (Oversold)'
        price_justification = 'The price has closed below the lower band, suggesting it is statistically cheap and could be due for a bounce.'

    return {
        'tool': 'Bollinger Bands',
        'volatility_signal': volatility_signal,
        'volatility_justification': volatility_justification,
        'price_position': price_position,
        'price_justification': price_justification,
        'details': {
            'Upper_Band': round(latest_upper, 2),
            'Lower_Band': round(latest_lower, 2),
            'Bandwidth_%': round(latest_bandwidth, 2),
        },
    }


@tool(
    name='get_vix_market_fear_signal',
    description='This tool analyzes the stock data for VIX market fear signals.',
    tool_hooks=[logger_hook],
)
def get_vix_market_fear_signal():
    try:
        vix = yf.Ticker('^VIX')
        vix_df = vix.history(period='1y')

        if 'Close' not in vix_df.columns or len(vix_df) < 6:
            return {
                'signal': 'Insufficient Data',
                'justification': 'Requires at least 6 data points for the VIX.',
                'details': {},
            }
    except Exception as e:
        return {
            'tool': 'VIX (Market Fear Gauge)',
            'signal': 'Data Fetch Error',
            'justification': f'Could not fetch VIX data: {e}',
            'details': {},
        }

    latest_vix = vix_df['Close'].iloc[-1]

    signal = 'Moderate Fear'
    justification = 'The VIX is between 20 and 30, suggesting a heightened level of uncertainty and caution in the overall market. Investors are wary.'
    if latest_vix < 20:
        signal = 'Low Fear (Complacency)'
        justification = 'The VIX is below 20, which typically indicates low volatility and investor confidence (complacency). This is generally positive for the market but can also precede corrections.'
    elif latest_vix >= 30:
        signal = 'High Fear (Panic)'
        justification = 'The VIX is at or above 30, signaling a high level of fear and uncertainty. This often occurs during market declines and periods of panic selling.'

    roc_5d = vix_df['Close'].pct_change(periods=5).iloc[-1] * 100
    volatility_of_fear = 'Stable'
    if roc_5d > 20:
        volatility_of_fear = 'Increasing Rapidly'
    elif roc_5d < -20:
        volatility_of_fear = 'Decreasing Rapidly'

    return {
        'tool': 'VIX (Market Fear Gauge)',
        'signal': signal,
        'justification': justification,
        'details': {
            'vix_level': round(latest_vix, 2),
            'volatility_of_fear': volatility_of_fear,
            'rate_of_change_5d_%': round(roc_5d, 2),
        },
    }
