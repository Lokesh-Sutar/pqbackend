from typing import Any

BROKER_FEES = {
    'zerodha': {
        'market': 'india',
        'equity_delivery': {
            'brokerage': 0.0,  # Free for delivery
            'brokerage_flat': 0.0,
            'stt': 0.001,  # 0.1% on sell side only
            'transaction_charges_nse': 0.0000345,  # 0.00345% NSE
            'transaction_charges_bse': 0.0000375,  # 0.00375% BSE
            'gst': 0.18,  # 18% on (brokerage + transaction charges)
            'sebi_charges': 0.00001,  # ₹10 per crore
            'stamp_duty': 0.00015,  # 0.015% on buy side
        },
        'equity_intraday': {
            'brokerage_pct': 0.0003,  # 0.03%
            'brokerage_flat_max': 20,  # ₹20 max per trade
            'stt': 0.00025,  # 0.025% on sell side
            'transaction_charges_nse': 0.0000345,
            'gst': 0.18,
            'sebi_charges': 0.00001,
            'stamp_duty': 0.00003,  # 0.003% on buy side
        },
    },
    'groww': {
        'market': 'india',
        'equity_delivery': {
            'brokerage_pct': 0.0005,  # 0.05%
            'brokerage_flat_max': 20,  # ₹20 max per trade
            'stt': 0.001,
            'transaction_charges_nse': 0.0000345,
            'transaction_charges_bse': 0.0000375,
            'gst': 0.18,
            'sebi_charges': 0.00001,
            'stamp_duty': 0.00015,
        },
        'equity_intraday': {
            'brokerage': 0.0,  # Free for intraday
            'brokerage_flat': 20,  # Flat ₹20 per trade
            'stt': 0.00025,
            'transaction_charges_nse': 0.0000345,
            'gst': 0.18,
            'sebi_charges': 0.00001,
            'stamp_duty': 0.00003,
        },
    },
    'angel_one': {
        'market': 'india',
        'equity_delivery': {
            'brokerage': 0.0,  # Free for delivery
            'brokerage_flat': 0.0,
            'stt': 0.001,
            'transaction_charges_nse': 0.0000345,
            'transaction_charges_bse': 0.0000375,
            'gst': 0.18,
            'sebi_charges': 0.00001,
            'stamp_duty': 0.00015,
        },
    },
    'upstox': {
        'market': 'india',
        'equity_delivery': {
            'brokerage': 0.0,  # Free for delivery
            'brokerage_flat': 0.0,
            'stt': 0.001,
            'transaction_charges_nse': 0.0000345,
            'gst': 0.18,
            'sebi_charges': 0.00001,
            'stamp_duty': 0.00015,
        },
    },
    'robinhood': {
        'market': 'us',
        'equity': {
            'commission': 0.0,  # Zero commission
            'sec_fee': 0.0000278,  # SEC fee $27.80 per $1M sold (as of 2024)
            'finra_taf': 0.000166,  # FINRA Trading Activity Fee $0.166 per $1000 sold
            'reg_fee': 0.0,  # No regulatory fee for buys
        },
    },
    'webull': {
        'market': 'us',
        'equity': {
            'commission': 0.0,
            'sec_fee': 0.0000278,
            'finra_taf': 0.000166,
            'reg_fee': 0.0,
        },
    },
    'interactive_brokers': {
        'market': 'us',
        'equity': {
            'commission_per_share': 0.005,  # $0.005 per share
            'commission_min': 1.0,  # Min $1 per order
            'commission_max_pct': 0.005,  # Max 0.5% of trade value
            'sec_fee': 0.0000278,
            'finra_taf': 0.000166,
        },
    },
}


def get_broker_info(broker: str) -> dict[str, Any]:
    """
    Get broker information

    Args:
        broker: Broker name

    Returns:
        dict with broker info or error
    """
    broker_lower = broker.lower().replace(' ', '_')
    if broker_lower in BROKER_FEES:
        return BROKER_FEES[broker_lower]
    return {'error': f'Broker "{broker}" not supported'}


def calculate_indian_broker_fees(
    broker: str,
    trade_type: str,
    quantity: int,
    price: float,
    trade_side: str,
    exchange: str = 'nse',
) -> dict[str, Any]:
    """
    Calculate transaction costs for Indian brokers

    Args:
        broker: Broker name (zerodha, groww, etc.)
        trade_type: 'delivery' or 'intraday'
        quantity: Number of shares
        price: Price per share
        trade_side: 'buy' or 'sell'
        exchange: 'nse' or 'bse'

    Returns:
        dict with fee breakdown
    """
    broker_lower = broker.lower().replace(' ', '_')
    if broker_lower not in BROKER_FEES:
        return {'error': f'Broker "{broker}" not supported', 'total_cost': 0}

    broker_info = BROKER_FEES[broker_lower]
    fee_structure = broker_info.get(
        f'equity_{trade_type}', broker_info.get('equity_delivery', {})
    )

    trade_value = quantity * price

    brokerage = 0.0
    if 'brokerage_pct' in fee_structure:
        brokerage = trade_value * fee_structure['brokerage_pct']
        if 'brokerage_flat_max' in fee_structure:
            brokerage = min(brokerage, fee_structure['brokerage_flat_max'])
    elif 'brokerage_flat' in fee_structure:
        brokerage = fee_structure['brokerage_flat']
    else:
        brokerage = trade_value * fee_structure.get('brokerage', 0.0)

    stt = 0.0
    if trade_side == 'sell':
        stt = trade_value * fee_structure.get('stt', 0.0)
    elif trade_type == 'intraday' and trade_side == 'buy':
        stt = trade_value * fee_structure.get('stt', 0.0)

    exchange_key = f'transaction_charges_{exchange.lower()}'
    transaction_charges = trade_value * fee_structure.get(
        exchange_key, fee_structure.get('transaction_charges_nse', 0.0)
    )

    gst_base = brokerage + transaction_charges
    gst = gst_base * fee_structure.get('gst', 0.18)

    sebi = trade_value * fee_structure.get('sebi_charges', 0.00001)

    stamp_duty = 0.0
    if trade_side == 'buy':
        stamp_duty = trade_value * fee_structure.get('stamp_duty', 0.00015)

    total_cost = brokerage + stt + transaction_charges + gst + sebi + stamp_duty

    return {
        'trade_value': round(trade_value, 2),
        'brokerage': round(brokerage, 2),
        'stt': round(stt, 2),
        'transaction_charges': round(transaction_charges, 2),
        'gst': round(gst, 2),
        'sebi_charges': round(sebi, 2),
        'stamp_duty': round(stamp_duty, 2),
        'total_cost': round(total_cost, 2),
        'cost_pct': round((total_cost / trade_value) * 100, 4) if trade_value > 0 else 0,
        'effective_price': round(
            price + (total_cost / quantity)
            if trade_side == 'buy'
            else price - (total_cost / quantity),
            2,
        ),
    }


def calculate_us_broker_fees(
    broker: str, quantity: int, price: float, trade_side: str
) -> dict[str, Any]:
    """
    Calculate transaction costs for US brokers

    Args:
        broker: Broker name (robinhood, webull, etc.)
        quantity: Number of shares
        price: Price per share
        trade_side: 'buy' or 'sell'

    Returns:
        dict with fee breakdown
    """
    broker_lower = broker.lower().replace(' ', '_')
    if broker_lower not in BROKER_FEES:
        return {'error': f'Broker "{broker}" not supported', 'total_cost': 0}

    broker_info = BROKER_FEES[broker_lower]
    fee_structure = broker_info.get('equity', {})

    trade_value = quantity * price

    commission = 0.0
    if 'commission_per_share' in fee_structure:
        commission = quantity * fee_structure['commission_per_share']
        commission = max(commission, fee_structure.get('commission_min', 0))
        if 'commission_max_pct' in fee_structure:
            commission = min(
                commission, trade_value * fee_structure['commission_max_pct']
            )
    else:
        commission = fee_structure.get('commission', 0.0)

    sec_fee = 0.0
    finra_taf = 0.0
    if trade_side == 'sell':
        sec_fee = trade_value * fee_structure.get('sec_fee', 0.0)
        finra_taf = trade_value * fee_structure.get('finra_taf', 0.0)

    total_cost = commission + sec_fee + finra_taf

    return {
        'trade_value': round(trade_value, 2),
        'commission': round(commission, 2),
        'sec_fee': round(sec_fee, 2),
        'finra_taf': round(finra_taf, 2),
        'total_cost': round(total_cost, 2),
        'cost_pct': round((total_cost / trade_value) * 100, 4) if trade_value > 0 else 0,
        'effective_price': round(
            price + (total_cost / quantity)
            if trade_side == 'buy'
            else price - (total_cost / quantity),
            2,
        ),
    }


def calculate_transaction_cost(
    broker: str,
    trade_type: str,
    quantity: int,
    price: float,
    trade_side: str,
    market: str = 'india',
    exchange: str = 'nse',
) -> dict[str, Any]:
    """
    Universal transaction cost calculator

    Args:
        broker: Broker name
        trade_type: 'delivery' or 'intraday' (India only)
        quantity: Number of shares
        price: Price per share
        trade_side: 'buy' or 'sell'
        market: 'india' or 'us'
        exchange: 'nse' or 'bse' (India only)

    Returns:
        dict with fee breakdown
    """
    if market.lower() == 'india':
        return calculate_indian_broker_fees(
            broker, trade_type, quantity, price, trade_side, exchange
        )
    elif market.lower() == 'us':
        return calculate_us_broker_fees(broker, quantity, price, trade_side)
    else:
        return {'error': f'Market "{market}" not supported', 'total_cost': 0}


def estimate_round_trip_cost(
    broker: str,
    trade_type: str,
    quantity: int,
    entry_price: float,
    exit_price: float,
    market: str = 'india',
) -> dict[str, Any]:
    """
    Calculate total cost for a complete trade (buy + sell)

    Args:
        broker: Broker name
        trade_type: 'delivery' or 'intraday'
        quantity: Number of shares
        entry_price: Entry/buy price
        exit_price: Exit/sell price
        market: 'india' or 'us'

    Returns:
        dict with round-trip cost breakdown
    """
    buy_cost = calculate_transaction_cost(
        broker, trade_type, quantity, entry_price, 'buy', market
    )

    sell_cost = calculate_transaction_cost(
        broker, trade_type, quantity, exit_price, 'sell', market
    )

    total_fees = buy_cost.get('total_cost', 0) + sell_cost.get('total_cost', 0)
    gross_profit = (exit_price - entry_price) * quantity
    net_profit = gross_profit - total_fees

    return {
        'entry_price': round(entry_price, 2),
        'exit_price': round(exit_price, 2),
        'quantity': quantity,
        'gross_profit': round(gross_profit, 2),
        'buy_costs': buy_cost,
        'sell_costs': sell_cost,
        'total_fees': round(total_fees, 2),
        'net_profit': round(net_profit, 2),
        'profit_reduced_by_pct': round((total_fees / abs(gross_profit)) * 100, 2)
        if gross_profit != 0
        else 0,
    }
