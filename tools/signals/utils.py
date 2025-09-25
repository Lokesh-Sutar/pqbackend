import pathlib
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd
import talib
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
    """Load ticker data from CSV file"""
    data_dir = Path(__file__).resolve().parent.parent.parent / 'data'
    df_file = data_dir / f'{ticker}.csv'

    try:
        df: pd.DataFrame = pd.read_csv(df_file)
        print(f'TICKER {ticker} IS LOADED FROM CSV')
        return df
    except FileNotFoundError:
        print(f'CSV file not found for {ticker}, attempting to fetch from yfinance')
        # Fallback to yfinance if CSV not available
        ticker_obj = yf.Ticker(ticker)
        df = ticker_obj.history(period='2y')  # Get 2 years of data
        df.columns = df.columns.str.lower()  # Normalize column names
        return df


def validate_data(
    df: DataFrame, required_columns: list, min_periods: int, tool_name: str
) -> dict | None:
    """Centralized data validation"""
    missing_cols = [col for col in required_columns if col not in df.columns]

    if missing_cols:
        return {
            'tool': tool_name,
            'signal': 'Insufficient Data',
            'justification': f'Missing required columns: {missing_cols}',
            'details': {},
        }

    if len(df) < min_periods:
        return {
            'tool': tool_name,
            'signal': 'Insufficient Data',
            'justification': f'Requires at least {min_periods} data points, got {len(df)}',
            'details': {},
        }

    return None
