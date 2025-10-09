"""RSI Mean Reversion strategy"""

import talib

from tools.advisory.strategies.base_strategy import BasePortfolioStrategy


class RSIMeanReversionStrategy(BasePortfolioStrategy):
    """
    RSI Mean Reversion strategy:
    - Buy when RSI drops below oversold threshold (default: 30)
    - Sell when RSI rises above overbought threshold (default: 70)
    - Works well in range-bound, volatile markets
    - Captures price extremes and reversions to mean

    Parameters:
    - rsi_period: Period for RSI calculation (default: 14)
    - oversold_threshold: RSI level to trigger buy (default: 30)
    - overbought_threshold: RSI level to trigger sell (default: 70)
    - use_stop_loss: Enable stop loss protection (default: True)
    """

    rsi_period = 14
    oversold_threshold = 30
    overbought_threshold = 70
    use_stop_loss = True

    def init(self):
        """Calculate RSI indicator using TA-Lib"""
        close_prices = self.data.Close
        self.rsi = self.I(talib.RSI, close_prices, timeperiod=self.rsi_period)

    def next(self):
        """Execute trading logic based on RSI mean reversion"""

        # Skip if RSI not yet calculated (need enough data points)
        if len(self.rsi) < self.rsi_period or self.rsi[-1] is None:
            return

        current_rsi = self.rsi[-1]

        # Entry logic: Buy when oversold
        if not self.position and current_rsi < self.oversold_threshold:
            # Calculate position size based on risk management
            size = self.calculate_position_size(self.data.Close[-1])
            if size > 0:
                self.buy(size=size)

        # Exit logic: Sell when overbought
        elif self.position and current_rsi > self.overbought_threshold:
            self.position.close()

        # Risk management: Stop loss check
        elif self.position and self.use_stop_loss and self.should_stop_out():
            self.position.close()
