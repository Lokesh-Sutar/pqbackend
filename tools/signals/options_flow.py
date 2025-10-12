import logging
from typing import Any, Dict

import yfinance as yf
from agno.tools import tool

logger: logging.Logger = logging.getLogger(__name__)


@tool(
    name='analyze_options_flow',
    description='Analyzes options volume and open interest to gauge institutional sentiment',
)
def analyze_options_flow(ticker: str) -> Dict[str, Any]:
    """
    Analyze options activity to understand smart money positioning

    Args:
        ticker: Stock symbol (e.g., 'AAPL', 'TSLA')

    Returns:
        Dict with options analysis and institutional sentiment
    """

    try:
        stock = yf.Ticker(ticker)

        try:
            exp_dates = stock.options
        except Exception:
            return {
                'signal': 'No Options Data',
                'ticker': ticker,
                'details': {
                    'warning': 'No options data available for this ticker',
                    'reason': 'Stock may not have listed options or data unavailable',
                    'recommendation': 'Use other indicators for this stock',
                },
            }

        if not exp_dates or len(exp_dates) == 0:
            return {
                'signal': 'No Options Data',
                'ticker': ticker,
                'details': {
                    'warning': 'No options expiration dates found',
                    'recommendation': 'Stock may not have active options trading',
                },
            }

        nearest_exp = exp_dates[0]
        options_chain = stock.option_chain(nearest_exp)
        calls = options_chain.calls
        puts = options_chain.puts

        if calls.empty or puts.empty:
            return {
                'signal': 'No Options Data',
                'ticker': ticker,
                'details': {
                    'warning': 'Options chain is empty',
                    'recommendation': 'Try different expiration or check later',
                },
            }

        call_volume = calls['volume'].sum()
        put_volume = puts['volume'].sum()

        if call_volume == 0:
            pc_ratio_volume = float('inf') if put_volume > 0 else 0
        else:
            pc_ratio_volume = put_volume / call_volume

        call_oi = calls['openInterest'].sum()
        put_oi = puts['openInterest'].sum()

        if call_oi == 0:
            pc_ratio_oi = float('inf') if put_oi > 0 else 0
        else:
            pc_ratio_oi = put_oi / call_oi

        call_iv_avg = calls['impliedVolatility'].mean() * 100
        put_iv_avg = puts['impliedVolatility'].mean() * 100
        iv_skew = put_iv_avg - call_iv_avg

        total_volume = call_volume + put_volume

        if pc_ratio_volume < 0.5:
            sentiment_volume = 'Very Bullish'
            volume_explanation = (
                'Heavy call buying (2x more calls than puts). Speculative optimism.'
            )
        elif pc_ratio_volume < 0.8:
            sentiment_volume = 'Bullish'
            volume_explanation = (
                'More call volume than puts. Moderate bullish positioning.'
            )
        elif pc_ratio_volume < 1.2:
            sentiment_volume = 'Neutral'
            volume_explanation = 'Balanced call/put volume. No clear directional bias.'
        elif pc_ratio_volume < 1.5:
            sentiment_volume = 'Bearish'
            volume_explanation = (
                'More put volume than calls. Moderate bearish positioning.'
            )
        else:
            sentiment_volume = 'Very Bearish'
            volume_explanation = 'Heavy put buying. Hedging or speculation on downside.'

        if pc_ratio_oi < 0.5:
            sentiment_oi = 'Very Bullish'
            oi_explanation = 'Mostly call positions. Long-term bullish positioning.'
        elif pc_ratio_oi < 0.8:
            sentiment_oi = 'Bullish'
            oi_explanation = 'More call open interest. Sustained bullish view.'
        elif pc_ratio_oi < 1.2:
            sentiment_oi = 'Neutral'
            oi_explanation = 'Balanced call/put open interest.'
        elif pc_ratio_oi < 1.5:
            sentiment_oi = 'Bearish'
            oi_explanation = 'More put open interest. Hedging or bearish positioning.'
        else:
            sentiment_oi = 'Very Bearish'
            oi_explanation = 'Heavy put positioning. Strong hedging or bearish bets.'

        if iv_skew > 10:
            skew_sentiment = 'Fear (Bearish)'
            skew_explanation = (
                'Puts more expensive than calls. Market pricing in downside risk.'
            )
        elif iv_skew > 3:
            skew_sentiment = 'Caution (Slightly Bearish)'
            skew_explanation = 'Slight put premium. Some hedging demand.'
        elif iv_skew < -10:
            skew_sentiment = 'Complacency (Bullish)'
            skew_explanation = (
                'Calls more expensive than puts. Little fear, high optimism.'
            )
        elif iv_skew < -3:
            skew_sentiment = 'Optimism (Slightly Bullish)'
            skew_explanation = 'Slight call premium. Speculative interest.'
        else:
            skew_sentiment = 'Neutral'
            skew_explanation = 'IV balanced between calls and puts.'

        bullish_signals = sum(
            [
                'Bullish' in sentiment_volume,
                'Bullish' in sentiment_oi,
                'Bullish' in skew_sentiment,
            ]
        )
        bearish_signals = sum(
            [
                'Bearish' in sentiment_volume,
                'Bearish' in sentiment_oi,
                'Bearish' in skew_sentiment,
            ]
        )

        if bullish_signals >= 2:
            overall_sentiment = 'Bullish'
            recommendation = 'Options flow suggests bullish positioning. Institutions/traders expect upside.'
        elif bearish_signals >= 2:
            overall_sentiment = 'Bearish'
            recommendation = 'Options flow suggests bearish/hedging activity. Caution or downside expected.'
        else:
            overall_sentiment = 'Mixed/Neutral'
            recommendation = (
                'Options flow is mixed. No clear directional bias from options market.'
            )

        info = stock.info
        current_price = info.get(
            'currentPrice', stock.history(period='1d')['Close'].iloc[-1]
        )

        result = {
            'signal': f'Options Sentiment: {overall_sentiment}',
            'ticker': ticker,
            'sentiment': overall_sentiment,
            'details': {
                'expiration_analyzed': nearest_exp,
                'current_price': round(current_price, 2),
                'volume_metrics': {
                    'total_volume': int(total_volume),
                    'call_volume': int(call_volume),
                    'put_volume': int(put_volume),
                    'put_call_ratio': float(round(pc_ratio_volume, 2)),
                    'sentiment': sentiment_volume,
                    'explanation': volume_explanation,
                },
                'open_interest_metrics': {
                    'total_open_interest': int(call_oi + put_oi),
                    'call_open_interest': int(call_oi),
                    'put_open_interest': int(put_oi),
                    'put_call_ratio': float(round(pc_ratio_oi, 2)),
                    'sentiment': sentiment_oi,
                    'explanation': oi_explanation,
                },
                'implied_volatility': {
                    'call_iv_avg_pct': float(round(call_iv_avg, 1)),
                    'put_iv_avg_pct': float(round(put_iv_avg, 1)),
                    'iv_skew': float(round(iv_skew, 1)),
                    'sentiment': skew_sentiment,
                    'explanation': skew_explanation,
                },
                'overall_sentiment': overall_sentiment,
                'recommendation': recommendation,
                'interpretation': f'Based on {nearest_exp} expiration: {overall_sentiment} sentiment. {recommendation}',
            },
        }

        return result

    except Exception as e:
        logger.error(f'Error analyzing options flow for {ticker}: {e}')
        return {
            'signal': 'Error',
            'ticker': ticker,
            'error': str(e),
            'recommendation': 'Use other indicators. Options data unavailable.',
        }
