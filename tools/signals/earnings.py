import logging
from datetime import datetime, timedelta
from typing import Any, Dict

import pandas as pd
import yfinance as yf
from agno.tools import tool

logger: logging.Logger = logging.getLogger(__name__)


@tool(
    name='check_earnings_calendar',
    description='Checks if earnings announcement is upcoming to warn about potential volatility',
)
def check_earnings_calendar(ticker: str) -> Dict[str, Any]:
    """
    Check if earnings announcement is coming soon and assess impact

    Args:
        ticker: Stock symbol (e.g., 'AAPL', 'RELIANCE.NS')

    Returns:
        Dict with earnings info and volatility warning
    """

    try:
        stock = yf.Ticker(ticker)

        calendar = stock.calendar

        is_empty = False
        if calendar is None:
            is_empty = True
        elif isinstance(calendar, dict):
            is_empty = len(calendar) == 0
        elif isinstance(calendar, pd.DataFrame):
            is_empty = calendar.empty
        else:
            is_empty = True

        if is_empty:
            info = stock.info
            earnings_date = info.get('earningsDate')

            if earnings_date is None:
                return {
                    'signal': 'No Earnings Data',
                    'ticker': ticker,
                    'details': {
                        'warning': 'No upcoming earnings date found',
                        'recommendation': 'Check company investor relations page for earnings schedule',
                    },
                }

        earnings_date = None

        if calendar is not None and not is_empty:
            if isinstance(calendar, dict):
                earnings_date = calendar.get('Earnings Date')
            elif isinstance(calendar, pd.DataFrame):
                if 'Earnings Date' in calendar.index:
                    earnings_date = calendar.loc['Earnings Date'].iloc[0]

        if earnings_date is None:
            info = stock.info
            if 'mostRecentQuarter' in info:
                last_earnings_timestamp = info.get('mostRecentQuarter')
                if last_earnings_timestamp:
                    last_earnings = datetime.fromtimestamp(last_earnings_timestamp)
                    estimated_next = last_earnings + timedelta(days=90)
                    earnings_date = estimated_next

        if earnings_date is None:
            return {
                'signal': 'No Earnings Data',
                'ticker': ticker,
                'details': {
                    'warning': 'Could not determine earnings date',
                    'recommendation': 'Manually check earnings calendar',
                },
            }

        if not isinstance(earnings_date, datetime):
            try:
                earnings_date = pd.to_datetime(earnings_date)
            except Exception:
                pass

        today = datetime.now()
        if isinstance(earnings_date, datetime):
            days_until = (earnings_date - today).days
        else:
            days_until = 30

        if days_until < 0:
            warning_level = 'Past Earnings'
            risk = 'Low'
            interpretation = f'Last earnings was {abs(days_until)} days ago. Post-earnings volatility likely settled.'
            recommendation = 'Safe to trade. Earnings volatility has passed.'
        elif days_until <= 7:
            warning_level = 'IMMINENT'
            risk = 'Very High'
            interpretation = (
                f'Earnings in {days_until} day(s)! Expect extreme volatility.'
            )
            recommendation = 'AVOID trading unless earnings-play. Wait for earnings to pass. Options IV crush risk.'
        elif days_until <= 14:
            warning_level = 'Very Soon'
            risk = 'High'
            interpretation = f'Earnings in {days_until} days. Volatility increasing.'
            recommendation = 'Reduce position size or wait. Market pricing in uncertainty. Consider IV spike if using options.'
        elif days_until <= 30:
            warning_level = 'Approaching'
            risk = 'Medium'
            interpretation = (
                f'Earnings in {days_until} days. Moderate volatility expected.'
            )
            recommendation = 'Can trade but monitor closely. Be prepared for increased swings as date nears.'
        else:
            warning_level = 'Far Away'
            risk = 'Low'
            interpretation = (
                f'Earnings in {days_until} days. Normal trading conditions.'
            )
            recommendation = (
                'Safe trading window. Earnings too far to impact current trades.'
            )

        info = stock.info
        pe_ratio = info.get('trailingPE', 'N/A')
        earnings_growth = info.get('earningsGrowth', 'N/A')

        if isinstance(earnings_date, datetime):
            earnings_date_str = earnings_date.strftime('%Y-%m-%d')
        elif isinstance(earnings_date, pd.DatetimeIndex):
            earnings_date_str = earnings_date[0].strftime('%Y-%m-%d')
        else:
            earnings_date_str = str(earnings_date)

        result = {
            'signal': f'Earnings: {warning_level}',
            'ticker': ticker,
            'warning_level': warning_level,
            'risk': risk,
            'details': {
                'earnings_date': earnings_date_str,
                'days_until_earnings': days_until,
                'warning_level': warning_level,
                'risk_level': risk,
                'interpretation': interpretation,
                'recommendation': recommendation,
                'context': {
                    'pe_ratio': pe_ratio if pe_ratio != 'N/A' else 'N/A',
                    'earnings_growth': f'{earnings_growth:.1%}'
                    if isinstance(earnings_growth, (int, float))
                    else 'N/A',
                },
            },
        }

        return result

    except Exception as e:
        logger.error(f'Error checking earnings calendar for {ticker}: {e}')
        return {
            'signal': 'Error',
            'ticker': ticker,
            'error': str(e),
            'recommendation': 'Manually check earnings calendar on Yahoo Finance or company IR page',
        }
