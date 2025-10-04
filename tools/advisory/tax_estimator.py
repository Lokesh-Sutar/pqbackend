"""Tax estimation for investment strategies"""

from typing import Any

TAX_RULES = {
    'india': {
        'short_term': {
            'threshold_days': 365,  # < 1 year
            'equity_gains_tax': 0.15,  # 15% STCG
            'description': 'Short-Term Capital Gains (< 1 year): 15% flat',
        },
        'long_term': {
            'equity_gains_tax': 0.10,  # 10% LTCG
            'exemption_limit': 100000,  # ₹1 lakh exempt per financial year
            'description': 'Long-Term Capital Gains (> 1 year): 10% above ₹1 lakh exemption',
        },
    },
    'us': {
        'short_term': {
            'threshold_days': 365,  # < 1 year
            'description': 'Short-Term Capital Gains (< 1 year): Taxed as ordinary income',
            'brackets_2024_single': [
                (0, 11600, 0.10),
                (11600, 47150, 0.12),
                (47150, 100525, 0.22),
                (100525, 191950, 0.24),
                (191950, 243725, 0.32),
                (243725, 609350, 0.35),
                (609350, float('inf'), 0.37),
            ],
            'brackets_2024_married': [
                (0, 23200, 0.10),
                (23200, 94300, 0.12),
                (94300, 201050, 0.22),
                (201050, 383900, 0.24),
                (383900, 487450, 0.32),
                (487450, 731200, 0.35),
                (731200, float('inf'), 0.37),
            ],
        },
        'long_term': {
            'brackets': [
                (0, 44625, 0.0),  # 0% for low income (single)
                (44625, 492300, 0.15),  # 15% for most
                (492300, float('inf'), 0.20),  # 20% for high income
            ],
            'description': 'Long-Term Capital Gains (> 1 year): 0%, 15%, or 20% based on income',
        },
    },
}


def estimate_indian_taxes(gains: float, holding_period_days: int) -> dict[str, Any]:
    """
    Estimate tax liability for Indian investors

    Args:
        gains: Total capital gains
        holding_period_days: Number of days position was held

    Returns:
        dict with tax breakdown
    """
    if gains <= 0:
        return {
            'taxable_gains': 0,
            'tax_liability': 0,
            'tax_rate': 0,
            'holding_period': 'N/A',
            'note': 'No tax on losses',
        }

    is_long_term = holding_period_days > 365

    if is_long_term:
        exemption = TAX_RULES['india']['long_term']['exemption_limit']
        taxable_gains = max(0, gains - exemption)
        tax_rate = TAX_RULES['india']['long_term']['equity_gains_tax']
        tax_liability = taxable_gains * tax_rate

        return {
            'holding_period': 'Long-term (> 1 year)',
            'total_gains': round(gains, 2),
            'exemption_used': round(min(gains, exemption), 2),
            'taxable_gains': round(taxable_gains, 2),
            'tax_rate': f'{tax_rate * 100}%',
            'tax_liability': round(tax_liability, 2),
            'effective_tax_rate': round((tax_liability / gains) * 100, 2)
            if gains > 0
            else 0,
            'note': TAX_RULES['india']['long_term']['description'],
        }
    else:
        tax_rate = TAX_RULES['india']['short_term']['equity_gains_tax']
        tax_liability = gains * tax_rate

        return {
            'holding_period': 'Short-term (< 1 year)',
            'total_gains': round(gains, 2),
            'taxable_gains': round(gains, 2),
            'tax_rate': f'{tax_rate * 100}%',
            'tax_liability': round(tax_liability, 2),
            'effective_tax_rate': round((tax_liability / gains) * 100, 2)
            if gains > 0
            else 0,
            'note': TAX_RULES['india']['short_term']['description'],
        }


def estimate_us_taxes(
    gains: float,
    holding_period_days: int,
    annual_income: float = 75000,
    filing_status: str = 'single',
) -> dict[str, Any]:
    """
    Estimate tax liability for US investors

    Args:
        gains: Total capital gains
        holding_period_days: Number of days position was held
        annual_income: Annual ordinary income (for STCG calculation)
        filing_status: 'single' or 'married'

    Returns:
        dict with tax breakdown
    """
    if gains <= 0:
        return {
            'taxable_gains': 0,
            'tax_liability': 0,
            'tax_rate': 0,
            'holding_period': 'N/A',
            'note': 'No tax on losses (can offset other gains)',
        }

    is_long_term = holding_period_days > 365

    if is_long_term:
        brackets = TAX_RULES['us']['long_term']['brackets']
        if annual_income <= brackets[0][1]:
            tax_rate = 0.0
        elif annual_income <= brackets[1][1]:
            tax_rate = 0.15
        else:
            tax_rate = 0.20

        tax_liability = gains * tax_rate

        return {
            'holding_period': 'Long-term (> 1 year)',
            'total_gains': round(gains, 2),
            'taxable_gains': round(gains, 2),
            'tax_rate': f'{tax_rate * 100}%',
            'tax_liability': round(tax_liability, 2),
            'effective_tax_rate': round((tax_liability / gains) * 100, 2)
            if gains > 0
            else 0,
            'note': TAX_RULES['us']['long_term']['description'],
            'income_bracket': f'Based on ${annual_income:,.0f} annual income',
        }
    else:
        bracket_key = f'brackets_2024_{filing_status}'
        brackets = TAX_RULES['us']['short_term'].get(
            bracket_key, TAX_RULES['us']['short_term']['brackets_2024_single']
        )
        taxable_income = annual_income + gains
        tax_on_total = calculate_progressive_tax(taxable_income, brackets)
        tax_on_income = calculate_progressive_tax(annual_income, brackets)
        tax_on_gains = tax_on_total - tax_on_income

        effective_rate = (tax_on_gains / gains * 100) if gains > 0 else 0

        return {
            'holding_period': 'Short-term (< 1 year)',
            'total_gains': round(gains, 2),
            'taxable_gains': round(gains, 2),
            'tax_rate': 'Ordinary income rates (progressive)',
            'marginal_rate': f'{find_marginal_rate(taxable_income, brackets) * 100}%',
            'tax_liability': round(tax_on_gains, 2),
            'effective_tax_rate': round(effective_rate, 2),
            'note': TAX_RULES['us']['short_term']['description'],
            'filing_status': filing_status,
        }


def calculate_progressive_tax(income: float, brackets: list) -> float:
    """
    Calculate tax using progressive tax brackets

    Args:
        income: Taxable income
        brackets: List of (lower, upper, rate) tuples

    Returns:
        Total tax
    """
    tax = 0.0
    for i, (lower, upper, rate) in enumerate(brackets):
        if income <= lower:
            break
        taxable_in_bracket = min(income, upper) - lower
        tax += taxable_in_bracket * rate
    return tax


def find_marginal_rate(income: float, brackets: list) -> float:
    """Find the marginal tax rate for given income"""
    for lower, upper, rate in brackets:
        if lower <= income < upper:
            return rate
    return brackets[-1][2]


def estimate_tax_impact(
    gains: float,
    holding_period_days: int,
    market: str = 'india',
    annual_income: float = 75000,
    filing_status: str = 'single',
) -> dict[str, Any]:
    """
    Universal tax estimator

    Args:
        gains: Total capital gains
        holding_period_days: Number of days position was held
        market: 'india' or 'us'
        annual_income: Annual income (for US only)
        filing_status: 'single' or 'married' (for US only)

    Returns:
        dict with tax estimation
    """
    if market.lower() == 'india':
        result = estimate_indian_taxes(gains, holding_period_days)
    elif market.lower() == 'us':
        result = estimate_us_taxes(
            gains, holding_period_days, annual_income, filing_status
        )
    else:
        return {'error': f'Market "{market}" not supported'}

    result['market'] = market
    result['disclaimer'] = (
        'Tax estimates are approximate. Consult a tax professional for accurate advice.'
    )

    return result


def compare_tax_efficiency(
    strategies: dict[str, dict], market: str = 'india'
) -> dict[str, Any]:
    """
    Compare tax efficiency across different strategies

    Args:
        strategies: dict of {strategy_name: {gains, holding_period_days, ...}}
        market: 'india' or 'us'

    Returns:
        dict with tax comparison
    """
    tax_comparison = {}

    for strategy_name, strategy_data in strategies.items():
        gains = strategy_data.get('total_return_amount', 0)
        holding_days = strategy_data.get('avg_holding_period_days', 365)

        tax_info = estimate_tax_impact(gains, holding_days, market)
        tax_comparison[strategy_name] = tax_info
    valid_strategies = {k: v for k, v in tax_comparison.items() if 'error' not in v}

    if valid_strategies:
        most_efficient = min(
            valid_strategies.items(), key=lambda x: x[1].get('effective_tax_rate', 100)
        )

        return {
            'comparison': tax_comparison,
            'most_tax_efficient': most_efficient[0],
            'tax_efficiency_note': f'{most_efficient[0]} has lowest effective tax rate at {most_efficient[1].get("effective_tax_rate", 0)}%',
        }

    return {'comparison': tax_comparison, 'most_tax_efficient': None}
