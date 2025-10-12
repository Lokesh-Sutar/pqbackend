from tools.advisory.strategies.base_strategy import BasePortfolioStrategy


class BuyAndHoldStrategy(BasePortfolioStrategy):
    """
    Buy and Hold strategy:
    - Buy at the start
    - Hold until the end
    - No stop loss, no exits

    This serves as the baseline for comparison.
    """

    def init(self):
        """No indicators needed for buy and hold"""
        self.bought = False

    def next(self):
        """Buy once at the beginning and hold"""
        if not self.position and not self.bought:
            self.buy()
            self.bought = True
