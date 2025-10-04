"""Dollar Cost Averaging strategy"""

from tools.advisory.strategies.base_strategy import BasePortfolioStrategy


class DollarCostAvgStrategy(BasePortfolioStrategy):
    """
    Dollar Cost Averaging (DCA) strategy:
    - Buy fixed amount at regular intervals
    - Reduces timing risk
    - Good for systematic investing

    Parameters:
    - investment_interval: Days between purchases (default: 21 for monthly)
    """

    investment_interval = 21

    def init(self):
        """Calculate buy schedule"""
        total_bars = len(self.data)
        num_purchases = max(1, total_bars // self.investment_interval)
        self.position_size = 1.0 / num_purchases
        self.buy_bars = set(range(0, total_bars, self.investment_interval))
        self.current_bar = 0

    def next(self):
        """Buy at regular intervals"""
        if self.current_bar in self.buy_bars:
            self.buy(size=self.position_size)

        self.current_bar += 1
