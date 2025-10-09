from tools.advisory.strategies.buy_and_hold import BuyAndHoldStrategy
from tools.advisory.strategies.dollar_cost_avg import DollarCostAvgStrategy
from tools.advisory.strategies.rsi_mean_reversion import RSIMeanReversionStrategy
from tools.advisory.strategies.sma_crossover import SMACrossoverStrategy

STRATEGY_REGISTRY = {
    'buy_and_hold': BuyAndHoldStrategy,
    'dollar_cost_avg': DollarCostAvgStrategy,
    'sma_crossover': SMACrossoverStrategy,
    'rsi_mean_reversion': RSIMeanReversionStrategy,
}

__all__ = [
    'BuyAndHoldStrategy',
    'DollarCostAvgStrategy',
    'SMACrossoverStrategy',
    'RSIMeanReversionStrategy',
    'STRATEGY_REGISTRY',
]
