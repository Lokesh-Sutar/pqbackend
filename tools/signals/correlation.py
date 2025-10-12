import logging
from typing import Any, Dict, List

import numpy as np
import pandas as pd
import yfinance as yf
from agno.tools import tool

logger: logging.Logger = logging.getLogger(__name__)


@tool(
    name='check_portfolio_correlation',
    description='Checks correlation between multiple stocks to identify diversification issues',
)
def check_portfolio_correlation(
    tickers: List[str], lookback_days: int = 90
) -> Dict[str, Any]:
    """
    Analyze correlation between stocks to assess diversification

    Args:
        tickers: List of stock symbols (e.g., ['AAPL', 'MSFT', 'GOOGL'])
        lookback_days: Days to analyze (default 90 for 3 months)

    Returns:
        Dict with correlation matrix and diversification assessment
    """

    try:
        if len(tickers) < 2:
            return {
                'signal': 'Error',
                'error': 'Need at least 2 tickers to check correlation',
            }

        data = {}
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period=f'{lookback_days}d')
                if not hist.empty and len(hist) >= 20:
                    data[ticker] = hist['Close']
            except Exception as e:
                logger.warning(f'Could not fetch data for {ticker}: {e}')

        if len(data) < 2:
            return {
                'signal': 'Insufficient Data',
                'error': f'Could only fetch data for {len(data)} ticker(s). Need at least 2.',
                'tickers_analyzed': list(data.keys()),
            }

        prices_df = pd.DataFrame(data)
        returns_df = prices_df.pct_change().dropna()

        correlation_matrix = returns_df.corr()

        high_correlations = []
        low_correlations = []

        for i in range(len(correlation_matrix)):
            for j in range(i + 1, len(correlation_matrix)):
                ticker1 = correlation_matrix.index[i]
                ticker2 = correlation_matrix.columns[j]
                corr_value = float(correlation_matrix.iloc[i, j])  # pyright: ignore[reportArgumentType]

                pair = {
                    'pair': f'{ticker1} - {ticker2}',
                    'correlation': float(round(corr_value, 3)),
                }

                if corr_value > 0.7:
                    high_correlations.append(pair)
                elif corr_value < 0.3:
                    low_correlations.append(pair)

        upper_triangle = correlation_matrix.where(
            np.triu(np.ones(correlation_matrix.shape), k=1).astype(bool)
        )
        avg_correlation = float(upper_triangle.stack().mean())  # type: ignore

        if avg_correlation > 0.7:
            diversification = 'Poor'
            risk_level = 'High'
            interpretation = 'Portfolio is highly concentrated. Most stocks move together. High downside risk.'
            recommendation = 'Add uncorrelated assets (different sectors, bonds, international) to reduce risk.'
        elif avg_correlation > 0.5:
            diversification = 'Moderate'
            risk_level = 'Medium'
            interpretation = (
                'Portfolio has some concentration. Stocks partially move together.'
            )
            recommendation = (
                'Consider adding more diverse assets to improve risk-adjusted returns.'
            )
        elif avg_correlation > 0.3:
            diversification = 'Good'
            risk_level = 'Low-Medium'
            interpretation = (
                'Portfolio is reasonably diversified. Some independence between stocks.'
            )
            recommendation = (
                'Diversification is adequate. Continue monitoring as markets change.'
            )
        else:
            diversification = 'Excellent'
            risk_level = 'Low'
            interpretation = 'Portfolio is well diversified. Stocks move independently.'
            recommendation = 'Strong diversification. Maintain this balance for optimal risk management.'

        corr_matrix_formatted = {}
        for ticker1 in correlation_matrix.index:
            corr_matrix_formatted[ticker1] = {}
            for ticker2 in correlation_matrix.columns:
                if ticker1 != ticker2:
                    corr_matrix_formatted[ticker1][ticker2] = float(
                        round(float(correlation_matrix.loc[ticker1, ticker2]), 3)  # pyright: ignore[reportArgumentType]
                    )

        result = {
            'signal': f'Diversification: {diversification}',
            'tickers_analyzed': list(data.keys()),
            'details': {
                'diversification_quality': diversification,
                'risk_level': risk_level,
                'average_correlation': float(round(avg_correlation, 3)),
                'correlation_matrix': corr_matrix_formatted,
                'high_correlations': high_correlations
                if high_correlations
                else ['None (good!)'],
                'low_correlations': low_correlations
                if low_correlations
                else ['None found'],
                'interpretation': interpretation,
                'recommendation': recommendation,
                'lookback_period': f'{lookback_days} days',
            },
        }

        return result

    except Exception as e:
        logger.error(f'Error checking portfolio correlation: {e}')
        return {'signal': 'Error', 'error': str(e)}
