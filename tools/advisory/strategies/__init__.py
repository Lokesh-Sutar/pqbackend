from tools.advisory.strategies.buy_and_hold import BuyAndHoldStrategy
from tools.advisory.strategies.dollar_cost_avg import DollarCostAvgStrategy
from tools.advisory.strategies.sma_crossover import SMACrossoverStrategy

STRATEGY_REGISTRY = {
    'buy_and_hold': BuyAndHoldStrategy,
    'dollar_cost_avg': DollarCostAvgStrategy,
    'sma_crossover': SMACrossoverStrategy,
}

__all__ = [
    'BuyAndHoldStrategy',
    'DollarCostAvgStrategy',
    'SMACrossoverStrategy',
    'STRATEGY_REGISTRY',
]
