import logging
from typing import Any, Dict

import yfinance as yf
from agno.tools import tool

logger = logging.getLogger(__name__)


SECTOR_ETFS = {
    'Technology': 'XLK',
    'Healthcare': 'XLV',
    'Financials': 'XLF',
    'Consumer Discretionary': 'XLY',
    'Consumer Staples': 'XLP',
    'Energy': 'XLE',
    'Utilities': 'XLU',
    'Real Estate': 'XLRE',
    'Materials': 'XLB',
    'Industrials': 'XLI',
    'Communication Services': 'XLC',
}


@tool(
    name='get_sector_performance',
    description='Compares stock performance to its sector to identify relative strength/weakness',
)
def get_sector_performance(ticker: str, lookback_days: int = 90) -> Dict[str, Any]:
    """
    Compare stock performance to its sector benchmark

    Args:
        ticker: Stock symbol (e.g., 'AAPL', 'JPM')
        lookback_days: Days to analyze (default 90 for 3 months)

    Returns:
        Dict with sector comparison and relative performance
    """

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        sector = info.get('sector', 'Unknown')

        if sector == 'Unknown' or sector not in SECTOR_ETFS:
            return {
                'signal': 'Sector Not Found',
                'ticker': ticker,
                'details': {
                    'warning': f'Sector "{sector}" not recognized or not available',
                    'recommendation': 'Cannot compare to sector. Evaluate stock independently.',
                },
            }

        sector_etf = SECTOR_ETFS[sector]

        stock_hist = stock.history(period=f'{lookback_days}d')
        sector_hist = yf.Ticker(sector_etf).history(period=f'{lookback_days}d')

        if stock_hist.empty or len(stock_hist) < 20:
            return {
                'signal': 'Insufficient Data',
                'ticker': ticker,
                'error': f'Insufficient stock data ({len(stock_hist)} days)',
            }

        if sector_hist.empty or len(sector_hist) < 20:
            return {
                'signal': 'Insufficient Data',
                'ticker': ticker,
                'error': f'Insufficient sector data for {sector_etf}',
            }

        stock_start = stock_hist['Close'].iloc[0]
        stock_end = stock_hist['Close'].iloc[-1]
        stock_return = ((stock_end - stock_start) / stock_start) * 100

        sector_start = sector_hist['Close'].iloc[0]
        sector_end = sector_hist['Close'].iloc[-1]
        sector_return = ((sector_end - sector_start) / sector_start) * 100

        relative_performance = stock_return - sector_return

        if relative_performance > 10:
            signal = 'Outperforming'
            strength = 'Strong'
            interpretation = f'{ticker} significantly outperforming its sector by {relative_performance:.1f}%'
            recommendation = 'Stock has strong momentum vs sector. Could continue if fundamentals support it.'
        elif relative_performance > 3:
            signal = 'Modestly Outperforming'
            strength = 'Moderate'
            interpretation = (
                f'{ticker} slightly outperforming sector by {relative_performance:.1f}%'
            )
            recommendation = 'Stock showing relative strength. Good sign but watch for sector trends.'
        elif relative_performance < -10:
            signal = 'Underperforming'
            strength = 'Weak'
            interpretation = f'{ticker} significantly underperforming sector by {abs(relative_performance):.1f}%'
            recommendation = 'Stock lagging sector. Investigate why: company-specific issues or buying opportunity?'
        elif relative_performance < -3:
            signal = 'Modestly Underperforming'
            strength = 'Weak-Moderate'
            interpretation = f'{ticker} slightly underperforming sector by {abs(relative_performance):.1f}%'
            recommendation = (
                'Stock trailing sector. Monitor for reversal or further weakness.'
            )
        else:
            signal = 'In Line with Sector'
            strength = 'Neutral'
            interpretation = f'{ticker} moving in line with sector ({relative_performance:+.1f}% difference)'
            recommendation = 'Stock tracking sector. Sector view applies to this stock.'

        company_name = info.get('longName', ticker)
        market_cap = info.get('marketCap', 0)
        market_cap_formatted = (
            f'${market_cap / 1e9:.1f}B'
            if market_cap > 1e9
            else f'${market_cap / 1e6:.1f}M'
            if market_cap > 1e6
            else 'N/A'
        )

        result = {
            'signal': signal,
            'ticker': ticker,
            'details': {
                'company_name': company_name,
                'sector': sector,
                'sector_benchmark': f'{sector_etf} (Sector ETF)',
                'lookback_period': f'{lookback_days} days',
                'stock_return_pct': float(round(stock_return, 2)),
                'sector_return_pct': float(round(sector_return, 2)),
                'relative_performance_pct': float(round(relative_performance, 2)),
                'relative_strength': strength,
                'interpretation': interpretation,
                'recommendation': recommendation,
                'context': {
                    'market_cap': market_cap_formatted,
                    'sector_trend': 'Bullish'
                    if sector_return > 5
                    else 'Bearish'
                    if sector_return < -5
                    else 'Neutral',
                },
            },
        }

        return result

    except Exception as e:
        logger.error(f'Error getting sector performance for {ticker}: {e}')
        return {'signal': 'Error', 'ticker': ticker, 'error': str(e)}
