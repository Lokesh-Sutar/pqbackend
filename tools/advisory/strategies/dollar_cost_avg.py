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

        if total_bars < self.investment_interval:
            self.position_size = 1.0
            self.buy_bars = {0}
            self.last_buy_bar = -1
            return

        num_purchases = max(1, total_bars // self.investment_interval)
        self.position_size = 1.0 / num_purchases
        self.buy_bars = set(range(0, total_bars, self.investment_interval))
        self.last_buy_bar = -1

    def next(self):
        """Buy at regular intervals"""
        current_bar = len(self.data) - 2

        if current_bar in self.buy_bars and current_bar != self.last_buy_bar:
            self.buy(size=self.position_size)
            self.last_buy_bar = current_bar
