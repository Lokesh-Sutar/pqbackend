from typing import Any, List

from agno.tools import tool
from backtesting import Backtest

from tools.advisory.data_handler import align_multiple_tickers, get_period_days
from tools.advisory.fee_calculator import estimate_round_trip_cost
from tools.advisory.risk_manager import get_risk_parameters
from tools.advisory.strategies import STRATEGY_REGISTRY
from tools.advisory.tax_estimator import estimate_tax_impact
from tools.helper import logger_hook


@tool(
    name='backtest_investment_strategies',
    description='Backtests multiple investment strategies (Buy and Hold, Dollar Cost Averaging, SMA Crossover) for given tickers over specified time horizons. Returns performance metrics, cost analysis, and tax implications for each strategy.',
    tool_hooks=[logger_hook],
)
def backtest_investment_strategies(
    tickers: List[str],
    capital: float = 10000,
    time_horizon: str = 'long',
    risk_profile: str = 'moderate',
    broker: str = 'zerodha',
    market: str = 'india',
) -> dict[str, Any]:
    """
    Backtest investment strategies for portfolio construction

    Args:
        tickers: List of stock ticker symbols (e.g., ['NVDA', 'AAPL', 'GOOGL'])
        capital: Total investment capital
        time_horizon: 'short' (1y), 'medium' (3y), or 'long' (5y)
        risk_profile: 'conservative', 'moderate', or 'aggressive'
        broker: Broker name for fee calculation (zerodha, groww, robinhood, etc.)
        market: 'india' or 'us'

    Returns:
        dict with strategy comparison, best recommendation, costs, and tax analysis
    """

    horizon_map = {'short': '1y', 'medium': '3y', 'long': '5y'}
    period = horizon_map.get(time_horizon.lower(), '5y')
    min_periods = 252

    risk_params = get_risk_parameters(risk_profile)

    try:
        data_result = align_multiple_tickers(tickers, period, min_periods)

        if not data_result['valid_tickers']:
            return {
                'tool': 'Strategy Backtester',
                'signal': 'Insufficient Data',
                'justification': 'Unable to load valid data for any ticker',
                'errors': data_result['errors'],
                'strategies': {},
            }

        valid_tickers = data_result['valid_tickers']
        ticker_data = data_result['data']

        warnings = []
        if len(valid_tickers) < len(tickers):
            failed = set(tickers) - set(valid_tickers)
            warnings.append(f'Unable to load data for: {", ".join(failed)}')

        if ticker_data:
            sample_ticker = list(ticker_data.keys())[0]
            actual_days = len(ticker_data[sample_ticker])
            expected_days = get_period_days(period)
            if actual_days < expected_days * 0.75:
                warnings.append(
                    f'Limited historical data available ({actual_days} days vs {expected_days} expected for {time_horizon} period). Results based on available data.'
                )

        all_results = {}
        strategies_to_test = ['buy_and_hold', 'dollar_cost_avg', 'sma_crossover']

        for strategy_name in strategies_to_test:
            strategy_class = STRATEGY_REGISTRY.get(strategy_name)

            if not strategy_class:
                continue

            cash_reserve = risk_params['cash_reserve']
            investable_capital = capital * (1 - cash_reserve)
            capital_per_ticker = investable_capital / len(valid_tickers)

            ticker_results = []

            for ticker in valid_tickers:
                df = ticker_data[ticker]

                try:
                    bt = Backtest(
                        df,
                        strategy_class,
                        cash=capital_per_ticker,
                        commission=0.0,
                        finalize_trades=True,  # Add this line
                        exclusive_orders=True,  # Add this line
                    )

                    stats = bt.run()

                    result = {
                        'ticker': ticker,
                        'total_return_pct': float(round(stats['Return [%]'], 2)),
                        'annual_return_pct': float(
                            round(stats.get('Return (Ann.) [%]', 0), 2)
                        ),
                        'sharpe_ratio': float(round(stats.get('Sharpe Ratio', 0), 2)),
                        'max_drawdown_pct': float(
                            round(stats.get('Max. Drawdown [%]', 0), 2)
                        ),
                        'num_trades': int(stats.get('# Trades', 0)),
                        'win_rate_pct': float(round(stats.get('Win Rate [%]', 0), 2)),
                        'final_value': float(round(stats['Equity Final [$]'], 2)),
                    }

                    ticker_results.append(result)

                except Exception as e:
                    warnings.append(
                        f'{ticker} backtest failed for {strategy_name}: {str(e)}'
                    )

            if ticker_results:
                total_final_value = sum(r['final_value'] for r in ticker_results)
                avg_return = sum(r['total_return_pct'] for r in ticker_results) / len(
                    ticker_results
                )
                avg_sharpe = sum(r['sharpe_ratio'] for r in ticker_results) / len(
                    ticker_results
                )
                worst_drawdown = min(r['max_drawdown_pct'] for r in ticker_results)
                total_trades = sum(r['num_trades'] for r in ticker_results)

                avg_price = 100
                total_fees = 0
                for result in ticker_results:
                    num_trades = result['num_trades']
                    if num_trades > 0:
                        fee_estimate = estimate_round_trip_cost(
                            broker, 'delivery', 10, avg_price, avg_price * 1.1, market
                        )
                        total_fees += fee_estimate.get('total_fees', 0) * (
                            num_trades / 2
                        )

                total_gains = total_final_value - investable_capital
                avg_holding_days = 365 if strategy_name == 'buy_and_hold' else 180
                tax_estimate = estimate_tax_impact(
                    total_gains, avg_holding_days, market
                )

                all_results[strategy_name] = {
                    'strategy': strategy_name.replace('_', ' ').title(),
                    'total_return_pct': round(avg_return, 2),
                    'annual_return_pct': round(
                        (
                            (
                                (total_final_value / investable_capital)
                                ** (1 / (int(period[0]) if period[0].isdigit() else 5))
                            )
                            - 1
                        )
                        * 100,
                        2,
                    ),
                    'sharpe_ratio': round(avg_sharpe, 2),
                    'max_drawdown_pct': round(worst_drawdown, 2),
                    'num_trades': total_trades,
                    'total_fees': round(total_fees, 2),
                    'estimated_tax': round(tax_estimate.get('tax_liability', 0), 2),
                    'final_value': round(total_final_value, 2),
                    'net_profit': round(
                        total_final_value
                        - investable_capital
                        - total_fees
                        - tax_estimate.get('tax_liability', 0),
                        2,
                    ),
                    'ticker_breakdown': ticker_results,
                }

        if all_results:
            ranked = sorted(
                all_results.items(),
                key=lambda x: x[1].get('sharpe_ratio', 0),
                reverse=True,
            )

            best_strategy = ranked[0][1]

            return {
                'tool': 'Strategy Backtester',
                'signal': 'Analysis Complete',
                'analysis_period': f'{time_horizon} term ({period})',
                'tickers_analyzed': valid_tickers,
                'capital': float(capital),
                'risk_profile': risk_profile,
                'investable_capital': float(round(investable_capital, 2)),
                'cash_reserve': float(round(capital * cash_reserve, 2)),
                'strategy_comparison': all_results,
                'recommendation': {
                    'best_strategy': best_strategy['strategy'],
                    'rationale': f'Highest risk-adjusted returns (Sharpe: {best_strategy["sharpe_ratio"]}) over {time_horizon} period',
                    'expected_return': f'{best_strategy["annual_return_pct"]}% annually',
                    'max_drawdown': f'{best_strategy["max_drawdown_pct"]}%',
                },
                'cost_analysis': {
                    'broker': broker,
                    'market': market,
                    'estimated_total_fees': round(best_strategy['total_fees'], 2),
                    'estimated_tax_liability': round(best_strategy['estimated_tax'], 2),
                },
                'warnings': warnings,
                'disclaimers': [
                    'Past performance does not guarantee future results',
                    'This is educational analysis, not financial advice',
                    'Backtests assume perfect execution and may not reflect real trading conditions',
                    'Consult a licensed financial advisor before investing',
                ],
            }
        else:
            return {
                'tool': 'Strategy Backtester',
                'signal': 'Error',
                'justification': 'All strategy backtests failed',
                'warnings': warnings,
                'strategies': {},
            }

    except Exception as e:
        return {
            'tool': 'Strategy Backtester',
            'signal': 'Error',
            'justification': f'Backtesting failed: {str(e)}',
            'strategies': {},
        }
