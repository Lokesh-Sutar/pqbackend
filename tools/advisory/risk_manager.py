from typing import Any, List

import numpy as np
import pandas as pd
import talib

RISK_PROFILES = {
    'conservative': {
        'max_position_size': 0.15,  # Max 15% per position
        'max_portfolio_risk': 0.10,  # Max 10% portfolio at risk
        'stop_loss_pct': 0.05,  # 5% stop loss
        'max_drawdown_tolerance': 0.15,  # Max 15% drawdown before reducing exposure
        'cash_reserve': 0.30,  # Keep 30% in cash
        'rebalance_threshold': 0.05,  # Rebalance when position drifts 5%
    },
    'moderate': {
        'max_position_size': 0.25,  # Max 25% per position
        'max_portfolio_risk': 0.15,  # Max 15% portfolio at risk
        'stop_loss_pct': 0.08,  # 8% stop loss
        'max_drawdown_tolerance': 0.25,  # Max 25% drawdown
        'cash_reserve': 0.15,  # Keep 15% in cash
        'rebalance_threshold': 0.10,
    },
    'aggressive': {
        'max_position_size': 0.40,  # Max 40% per position
        'max_portfolio_risk': 0.25,  # Max 25% portfolio at risk
        'stop_loss_pct': 0.12,  # 12% stop loss
        'max_drawdown_tolerance': 0.35,  # Max 35% drawdown
        'cash_reserve': 0.05,  # Keep 5% in cash
        'rebalance_threshold': 0.15,
    },
}


def get_risk_parameters(risk_profile: str) -> dict[str, float]:
    """
    Get risk parameters for a given profile

    Args:
        risk_profile: 'conservative', 'moderate', or 'aggressive'

    Returns:
        dict with risk parameters
    """
    return RISK_PROFILES.get(risk_profile.lower(), RISK_PROFILES['moderate'])


def calculate_position_size_by_risk(
    capital: float, entry_price: float, stop_loss_price: float, risk_per_trade: float
) -> int:
    """
    Calculate exact shares based on risk tolerance
    Formula: Shares = (Capital × Risk%) ÷ (Entry - Stop)

    Args:
        capital: Total portfolio capital
        entry_price: Entry price per share
        stop_loss_price: Stop loss price per share
        risk_per_trade: Percentage of capital to risk (e.g., 0.02 for 2%)

    Returns:
        Number of shares to buy
    """
    if entry_price <= 0 or stop_loss_price <= 0:
        return 0

    risk_amount = capital * risk_per_trade
    risk_per_share = abs(entry_price - stop_loss_price)

    if risk_per_share == 0:
        return 0

    shares = int(risk_amount / risk_per_share)
    return shares


def calculate_volatility_adjusted_size(
    df: pd.DataFrame, capital: float, max_position_size: float, atr_period: int = 14
) -> dict[str, Any]:
    """
    Calculate position size adjusted for volatility using ATR
    Lower volatility = larger position, Higher volatility = smaller position

    Args:
        df: DataFrame with OHLC data
        capital: Total portfolio capital
        max_position_size: Maximum percentage of capital per position
        atr_period: Period for ATR calculation

    Returns:
        dict with position size info
    """
    if len(df) < atr_period + 1:
        return {
            'shares': 0,
            'position_size': 0,
            'atr': 0,
            'error': 'Insufficient data for ATR calculation',
        }

    try:
        high_prices = df['high'].to_numpy(dtype=float)
        low_prices = df['low'].to_numpy(dtype=float)
        close_prices = df['close'].to_numpy(dtype=float)
        atr = talib.ATR(high_prices, low_prices, close_prices, timeperiod=atr_period)

        current_atr = atr[-1]
        current_price = df['close'].iloc[-1]

        if current_atr == 0 or np.isnan(current_atr):
            return {
                'shares': 0,
                'position_size': 0,
                'atr': 0,
                'error': 'Invalid ATR value',
            }

        atr_pct = (current_atr / current_price) * 100

        volatility_multiplier = min(1.0, 2.0 / (atr_pct + 2.0))  # Caps at 1.0

        adjusted_position_size = max_position_size * volatility_multiplier
        position_value = capital * adjusted_position_size
        shares = int(position_value / current_price)

        return {
            'shares': shares,
            'position_value': round(position_value, 2),
            'position_size_pct': round(adjusted_position_size * 100, 2),
            'atr': round(current_atr, 2),
            'atr_pct': round(atr_pct, 2),
            'volatility_multiplier': round(volatility_multiplier, 2),
            'current_price': round(current_price, 2),
        }

    except Exception as e:
        return {
            'shares': 0,
            'position_size': 0,
            'atr': 0,
            'error': f'ATR calculation failed: {str(e)}',
        }


def calculate_equal_weight_allocation(
    tickers: List[str], capital: float, cash_reserve: float
) -> dict[str, float]:
    """
    Simple equal-weight allocation across tickers

    Args:
        tickers: List of ticker symbols
        capital: Total capital
        cash_reserve: Percentage to keep in cash (e.g., 0.15 for 15%)

    Returns:
        dict with allocation per ticker
    """
    investable_capital = capital * (1 - cash_reserve)
    allocation_per_ticker = investable_capital / len(tickers)

    return {ticker: allocation_per_ticker for ticker in tickers}


def diversification_check(
    tickers: List[str], allocations: dict[str, float]
) -> dict[str, Any]:
    """
    Check diversification and warn about concentration risks

    Args:
        tickers: List of ticker symbols
        allocations: dict of {ticker: allocation_amount}

    Returns:
        dict with diversification analysis and warnings
    """
    warnings = []
    total_invested = sum(allocations.values())

    num_positions = len(tickers)
    if num_positions < 3:
        warnings.append(
            f'Portfolio has only {num_positions} positions. Consider adding more for better diversification.'
        )

    for ticker, allocation in allocations.items():
        allocation_pct = (allocation / total_invested) * 100 if total_invested > 0 else 0
        if allocation_pct > 40:
            warnings.append(
                f'{ticker} represents {allocation_pct:.1f}% of portfolio - high concentration risk'
            )

    if num_positions >= 5:
        diversification_status = 'Good'
    elif num_positions >= 3:
        diversification_status = 'Moderate'
    else:
        diversification_status = 'Limited'

    return {
        'status': diversification_status,
        'num_positions': num_positions,
        'warnings': warnings,
    }


def calculate_stop_loss_level(entry_price: float, stop_loss_pct: float) -> float:
    """
    Calculate stop loss price based on percentage

    Args:
        entry_price: Entry price per share
        stop_loss_pct: Stop loss percentage (e.g., 0.08 for 8%)

    Returns:
        Stop loss price
    """
    return entry_price * (1 - stop_loss_pct)


def apply_position_limits(
    shares: int, price: float, capital: float, max_position_size: float
) -> dict[str, Any]:
    """
    Apply position size limits to ensure risk constraints

    Args:
        shares: Calculated number of shares
        price: Current price per share
        capital: Total portfolio capital
        max_position_size: Maximum percentage of capital per position

    Returns:
        dict with adjusted shares and details
    """
    position_value = shares * price
    position_pct = (position_value / capital) * 100 if capital > 0 else 0

    max_value = capital * max_position_size
    max_shares = int(max_value / price)

    if shares > max_shares:
        return {
            'shares': max_shares,
            'position_value': round(max_shares * price, 2),
            'position_pct': round(max_position_size * 100, 2),
            'limited': True,
            'reason': f'Reduced from {shares} to {max_shares} shares due to max position size limit',
        }

    return {
        'shares': shares,
        'position_value': round(position_value, 2),
        'position_pct': round(position_pct, 2),
        'limited': False,
        'reason': 'Within position size limits',
    }
