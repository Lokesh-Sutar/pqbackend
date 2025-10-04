from typing import Any, List

import yfinance as yf
from agno.tools import tool

from tools.advisory.data_handler import load_ticker_data
from tools.advisory.fee_calculator import calculate_transaction_cost
from tools.advisory.risk_manager import (
    apply_position_limits,
    calculate_volatility_adjusted_size,
    diversification_check,
    get_risk_parameters,
)
from tools.helper import logger_hook


@tool(
    name='build_portfolio_allocation',
    description='Generates detailed portfolio allocation recommendations with exact share counts, position sizing based on risk profile, entry strategies, and rebalancing guidance. Provides actionable investment plan.',
    tool_hooks=[logger_hook],
)
def build_portfolio_allocation(
    tickers: List[str],
    capital: float = 10000,
    risk_profile: str = 'moderate',
    selected_strategy: str = 'buy_and_hold',
    broker: str = 'zerodha',
    market: str = 'india',
) -> dict[str, Any]:
    """
    Generate portfolio allocation with actionable recommendations

    Args:
        tickers: List of stock ticker symbols
        capital: Total investment capital
        risk_profile: 'conservative', 'moderate', or 'aggressive'
        selected_strategy: Strategy to use for entry (buy_and_hold, dollar_cost_avg, etc.)
        broker: Broker name for fee calculation
        market: 'india' or 'us'

    Returns:
        dict with allocation details, share counts, costs, and recommendations
    """

    risk_params = get_risk_parameters(risk_profile)
    cash_reserve = risk_params['cash_reserve']
    max_position_size = risk_params['max_position_size']
    stop_loss_pct = risk_params['stop_loss_pct']

    investable_capital = capital * (1 - cash_reserve)
    cash_reserve_amount = capital * cash_reserve

    try:
        allocations = {}
        total_allocated = 0
        failed_tickers = []

        for ticker in tickers:
            try:
                df = load_ticker_data(ticker, period='1y')

                if df.empty or len(df) < 20:
                    failed_tickers.append(ticker)
                    continue

                current_price = df['close'].iloc[-1]

                vol_info = calculate_volatility_adjusted_size(
                    df, investable_capital, max_position_size, atr_period=14
                )

                if vol_info.get('error'):
                    position_value = investable_capital / len(tickers)
                    shares = int(position_value / current_price)
                    vol_info = {
                        'shares': shares,
                        'position_value': position_value,
                        'position_size_pct': (position_value / capital) * 100,
                        'atr': 0,
                        'atr_pct': 0,
                        'current_price': current_price,
                    }

                limited_info = apply_position_limits(
                    vol_info['shares'], current_price, capital, max_position_size
                )

                shares = limited_info['shares']
                actual_cost = shares * current_price

                stop_loss_price = current_price * (1 - stop_loss_pct)

                buy_cost = calculate_transaction_cost(
                    broker, 'delivery', shares, current_price, 'buy', market
                )

                allocations[ticker] = {
                    'current_price': float(round(current_price, 2)),
                    'recommended_shares': int(shares),
                    'actual_cost': float(round(actual_cost, 2)),
                    'target_weight_pct': float(
                        round((actual_cost / investable_capital) * 100, 2)
                    ),
                    'stop_loss_price': float(round(stop_loss_price, 2)),
                    'stop_loss_pct': float(round(stop_loss_pct * 100, 2)),
                    'volatility_pct': float(round(vol_info.get('atr_pct', 0), 2)),
                    'transaction_fees': float(round(buy_cost.get('total_cost', 0), 2)),
                    'effective_price': float(
                        round(buy_cost.get('effective_price', current_price), 2)
                    ),
                }

                total_allocated += actual_cost

            except Exception as e:
                failed_tickers.append(f'{ticker} ({str(e)})')

        if not allocations:
            return {
                'tool': 'Portfolio Allocator',
                'signal': 'Error',
                'justification': 'Unable to generate allocations for any ticker',
                'failed_tickers': failed_tickers,
                'allocation': {},
            }

        total_fees = float(sum(a['transaction_fees'] for a in allocations.values()))
        remaining_cash = float(capital - total_allocated - total_fees)

        div_check = diversification_check(
            list(allocations.keys()),
            {k: v['actual_cost'] for k, v in allocations.items()},
        )

        entry_strategies = {
            'buy_and_hold': {
                'approach': 'Lump Sum Entry',
                'description': 'Invest full allocated amount immediately',
                'rationale': 'Time in market beats timing the market for long-term investing',
                'steps': [
                    'Place limit orders at or near current market price',
                    'Set stop-loss orders at calculated levels',
                    'Review positions after market close',
                ],
            },
            'dollar_cost_avg': {
                'approach': 'Systematic Investment (DCA)',
                'description': 'Split investment into 3-4 tranches over 2-3 months',
                'rationale': 'Reduces timing risk and smooths entry price',
                'steps': [
                    'Invest 25% of allocation now',
                    'Invest 25% after 3 weeks',
                    'Invest 25% after 6 weeks',
                    'Invest remaining 25% after 9 weeks',
                ],
            },
            'sma_crossover': {
                'approach': 'Technical Entry',
                'description': 'Enter when stocks are in uptrend (price above 50-day MA)',
                'rationale': 'Momentum-based entry aligns with trend-following strategy',
                'steps': [
                    'Wait for price to be above 50-day moving average',
                    'Enter with 50% of allocation on golden cross',
                    'Add remaining 50% if uptrend confirms',
                ],
            },
        }

        selected_entry = entry_strategies.get(
            selected_strategy, entry_strategies['buy_and_hold']
        )

        rebalance_threshold = risk_params['rebalance_threshold']
        rebalance_guidance = {
            'frequency': 'Quarterly'
            if risk_profile == 'moderate'
            else 'Monthly'
            if risk_profile == 'aggressive'
            else 'Semi-annually',
            'trigger': f'When any position deviates more than {rebalance_threshold * 100}% from target weight',
            'method': 'Sell overweight positions and buy underweight positions to restore target allocations',
        }

        return {
            'tool': 'Portfolio Allocator',
            'signal': 'Allocation Complete',
            'risk_profile': risk_profile,
            'strategy': selected_strategy.replace('_', ' ').title(),
            'total_capital': float(capital),
            'investable_capital': float(round(investable_capital, 2)),
            'cash_reserve': float(round(cash_reserve_amount, 2)),
            'allocation': allocations,
            'summary': {
                'total_allocated': float(round(total_allocated, 2)),
                'total_transaction_fees': float(round(total_fees, 2)),
                'remaining_cash': float(round(remaining_cash, 2)),
                'number_of_positions': int(len(allocations)),
                'diversification_status': div_check['status'],
                'diversification_warnings': div_check['warnings'],
            },
            'entry_strategy': selected_entry,
            'rebalancing': rebalance_guidance,
            'risk_management': {
                'max_position_size': f'{max_position_size * 100}%',
                'stop_loss_default': f'{stop_loss_pct * 100}%',
                'position_sizing_method': 'Volatility-adjusted (ATR-based)',
            },
            'warnings': [f'Could not process: {ticker}' for ticker in failed_tickers]
            if failed_tickers
            else [],
            'next_steps': [
                f'Open account with {broker} if not already done',
                'Fund account with at least ₹{:,.2f}'.format(total_allocated + total_fees)
                if market == 'india'
                else 'Fund account with at least ${:,.2f}'.format(
                    total_allocated + total_fees
                ),
                'Review allocation and adjust if needed',
                'Place orders according to entry strategy',
                'Set alerts for stop-loss levels',
                'Schedule first rebalancing review',
            ],
            'disclaimers': [
                'This is educational guidance, not financial advice',
                'Past performance does not guarantee future results',
                'Consider your personal financial situation and risk tolerance',
                'Consult with a licensed financial advisor before investing',
            ],
        }

    except Exception as e:
        return {
            'tool': 'Portfolio Allocator',
            'signal': 'Error',
            'justification': f'Allocation failed: {str(e)}',
            'allocation': {},
        }
