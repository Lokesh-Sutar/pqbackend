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

        if len(self.rsi) < self.rsi_period:
            return

        current_rsi = self.rsi[-1]

        if current_rsi is None or (
            hasattr(current_rsi, '__iter__') and len(current_rsi) == 0
        ):
            return

        try:
            current_rsi = float(current_rsi)
        except (ValueError, TypeError):
            return

        if not self.position and current_rsi < self.oversold_threshold:
            size = self.calculate_position_size(self.data.Close[-1])
            if size > 0:
                self.buy(size=size)

        elif self.position and current_rsi > self.overbought_threshold:
            self.position.close()

        elif self.position and self.use_stop_loss and self.should_stop_out():
            self.position.close()
