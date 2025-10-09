import logging
from typing import Any, List, Tuple

import pandas as pd
import yfinance as yf

from tools.helper import get_ticker

logger = logging.getLogger(__name__)


def load_ticker_data(ticker: str, period: str = '5y') -> pd.DataFrame:
    """
    Load ticker data from CSV (via utils.get_ticker) or yfinance
    Ensures standard OHLCV format with lowercase columns

    Args:
        ticker: Stock ticker symbol
        period: Time period ('1y', '2y', '5y', 'max')

    Returns:
        DataFrame with columns: ['date', 'open', 'high', 'low', 'close', 'volume']
    """
    try:
        df = get_ticker(ticker)

        df.columns = df.columns.str.lower()
        if 'date' not in df.columns and not isinstance(df.index, pd.DatetimeIndex):
            if (
                df.index.name
                and isinstance(df.index.name, str)
                and 'date' in df.index.name.lower()
            ):
                df.reset_index(inplace=True)
                df.columns = df.columns.str.lower()
        required = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in df.columns for col in required):
            raise ValueError('Missing required OHLCV columns')

        return df

    except Exception as e:
        logger.info(f'Failed to load {ticker} from CSV: {e}. Fetching from yfinance...')
        ticker_obj = yf.Ticker(ticker)
        df = ticker_obj.history(period=period)

        if df.empty:
            raise ValueError(f'No data available for {ticker}')
        df.columns = df.columns.str.lower()
        df.reset_index(inplace=True)
        if 'date' not in df.columns:
            date_col = [c for c in df.columns if 'date' in c.lower()]
            if date_col:
                df.rename(columns={date_col[0]: 'date'}, inplace=True)

        return df


def validate_ohlcv_data(
    df: pd.DataFrame, ticker: str, min_periods: int = 252
) -> Tuple[bool, str]:
    """
    Validate OHLCV data quality and sufficiency

    Args:
        df: DataFrame to validate
        ticker: Ticker symbol (for error messages)
        min_periods: Minimum number of data points required

    Returns:
        Tuple of (is_valid, error_message)
    """
    if df.empty:
        return False, f'{ticker}: DataFrame is empty'

    required_columns = ['open', 'high', 'low', 'close', 'volume']
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        return False, f'{ticker}: Missing required columns: {missing_columns}'

    if len(df) < min_periods:
        return (
            False,
            f'{ticker}: Insufficient data - has {len(df)} rows, needs at least {min_periods}',
        )

    critical_cols = ['open', 'high', 'low', 'close']
    null_counts = df[critical_cols].isnull().sum()

    if null_counts.any():
        null_info = null_counts[null_counts > 0].to_dict()
        return False, f'{ticker}: Null values found in columns: {null_info}'

    for col in critical_cols:
        if (df[col] <= 0).any():
            return (
                False,
                f'{ticker}: Invalid (zero/negative) prices found in column: {col}',
            )

    if (df['high'] < df['low']).any():
        return False, f'{ticker}: High price is less than low price in some rows'

    return True, ''


def prepare_backtest_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare DataFrame for backtesting.py library
    Ensures proper format and column names

    Args:
        df: Raw OHLCV DataFrame

    Returns:
        DataFrame formatted for backtesting.py
    """
    bt_df = df.copy()
    if 'date' in bt_df.columns:
        bt_df['date'] = pd.to_datetime(bt_df['date'])
        bt_df.set_index('date', inplace=True)

    column_mapping = {
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume',
    }

    bt_df.rename(columns=column_mapping, inplace=True)
    bt_df.sort_index(inplace=True)
    bt_df = bt_df[~bt_df.index.duplicated(keep='first')]

    return bt_df


def align_multiple_tickers(
    tickers: List[str], period: str = '5y', min_periods: int = 252
) -> dict[str, Any]:
    """
    Load and align data for multiple tickers
    Handles different trading calendars and data availability

    Args:
        tickers: List of ticker symbols
        period: Time period to load
        min_periods: Minimum required data points

    Returns:
        dict with {
            'data': {ticker: DataFrame},
            'errors': {ticker: error_message},
            'common_start_date': earliest common date,
            'common_end_date': latest common date
        }
    """
    result = {'data': {}, 'errors': {}, 'valid_tickers': []}

    all_dates = []

    for ticker in tickers:
        try:
            df = load_ticker_data(ticker, period)
            is_valid, error_msg = validate_ohlcv_data(df, ticker, min_periods)

            if not is_valid:
                result['errors'][ticker] = error_msg
                continue
            bt_df = prepare_backtest_data(df)

            result['data'][ticker] = bt_df
            result['valid_tickers'].append(ticker)
            all_dates.append((bt_df.index.min(), bt_df.index.max()))

        except Exception as e:
            result['errors'][ticker] = f'Failed to load {ticker}: {str(e)}'
    if all_dates:
        result['common_start_date'] = max(start for start, _ in all_dates)
        result['common_end_date'] = min(end for _, end in all_dates)
    else:
        result['common_start_date'] = None
        result['common_end_date'] = None

    return result


def get_period_days(period: str) -> int:
    """
    Convert period string to approximate trading days

    Args:
        period: Period string ('1y', '3y', '5y')

    Returns:
        Approximate number of trading days
    """
    period_map = {
        '1y': 252,
        'short': 252,
        '2y': 504,
        '3y': 756,
        'medium': 756,
        '5y': 1260,
        'long': 1260,
        '10y': 2520,
        'max': 5000,
    }

    return period_map.get(period.lower(), 1260)


def calculate_data_quality_score(df: pd.DataFrame) -> dict[str, Any]:
    """
    Calculate a quality score for the data

    Args:
        df: OHLCV DataFrame

    Returns:
        dict with quality metrics
    """
    score = 100
    issues = []
    if isinstance(df.index, pd.DatetimeIndex):
        date_diff = df.index.to_series().diff()
        # Convert to days, handling potential NaT values
        days_diff = date_diff.dt.days
        days_diff_clean = days_diff.dropna()

        if len(days_diff_clean) > 0:
            avg_gap = days_diff_clean.median()

            if avg_gap > 3:
                score -= 10
                issues.append(f'Data has gaps (avg {avg_gap:.1f} days between records)')
    if 'volume' in df.columns or 'Volume' in df.columns:
        vol_col = 'volume' if 'volume' in df.columns else 'Volume'
        zero_volume_pct = (df[vol_col] == 0).sum() / len(df) * 100

        if zero_volume_pct > 5:
            score -= 15
            issues.append(f'{zero_volume_pct:.1f}% of days have zero volume')

    close_col = 'close' if 'close' in df.columns else 'Close'
    returns = df[close_col].pct_change()
    extreme_moves = (abs(returns) > 0.20).sum()

    if extreme_moves > len(df) * 0.01:
        score -= 10
        issues.append(f'{extreme_moves} extreme price moves detected')

    quality_rating = (
        'Excellent'
        if score >= 90
        else 'Good'
        if score >= 75
        else 'Fair'
        if score >= 60
        else 'Poor'
    )

    return {'score': score, 'rating': quality_rating, 'issues': issues}
