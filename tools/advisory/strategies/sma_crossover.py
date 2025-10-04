"""SMA Crossover strategy using TA-Lib"""

import talib
from backtesting import Strategy
from backtesting.lib import crossover

from tools.advisory.strategies.base_strategy import BasePortfolioStrategy


class SMACrossoverStrategy(BasePortfolioStrategy):
    """
    Simple Moving Average Crossover strategy:
    - Buy when fast SMA crosses above slow SMA (golden cross)
    - Sell when fast SMA crosses below slow SMA (death cross)
    - Classic trend-following approach

    Parameters:
    - fast_period: Period for fast SMA (default: 50)
    - slow_period: Period for slow SMA (default: 200)
    """

    fast_period = 50
    slow_period = 200

    def init(self):
        """Calculate moving averages using TA-Lib"""
        close_prices = self.data.Close
        self.sma_fast = self.I(talib.SMA, close_prices, timeperiod=self.fast_period)
        self.sma_slow = self.I(talib.SMA, close_prices, timeperiod=self.slow_period)

    def next(self):
        """Execute trading logic based on SMA crossover"""
        if crossover(self.sma_fast, self.sma_slow):  # pyright: ignore[reportArgumentType]
            # Fast MA crosses above slow MA - BUY
            if not self.position:
                self.buy()
        elif crossover(self.sma_slow, self.sma_fast):  # pyright: ignore[reportArgumentType]
            if self.position:
                self.position.close()

        # Optional: Implement stop loss
        elif self.position and self.should_stop_out():
            self.position.close()
