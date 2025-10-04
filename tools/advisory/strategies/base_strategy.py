from backtesting import Strategy


class BasePortfolioStrategy(Strategy):
    """
    Base class that all portfolio strategies inherit from
    Provides common risk management and position sizing logic

    Subclasses should override:
    - init(): Set up indicators
    - next(): Implement entry/exit logic
    """

    risk_per_trade = 0.02  # 2% risk per trade
    stop_loss_pct = 0.08  # 8% stop loss
    take_profit_pct = None  # No take profit by default

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def calculate_position_size(self, price: float, stop_loss: float = None) -> float:  # pyright: ignore[reportArgumentType]
        """
        Calculate position size based on risk management
        Formula: Position Size = (Capital * Risk%) / (Entry - Stop Loss)

        Args:
            price: Current entry price
            stop_loss: Stop loss price (if None, uses stop_loss_pct)

        Returns:
            Fraction of capital to risk (0.0 to 1.0)
        """
        if stop_loss is None:
            stop_loss = price * (1 - self.stop_loss_pct)

        risk_amount = self.equity * self.risk_per_trade
        risk_per_share = abs(price - stop_loss)

        if risk_per_share == 0:
            return 0.0

        shares = risk_amount / risk_per_share
        position_value = shares * price

        fraction = min(1.0, position_value / self.equity)
        return fraction

    def set_stop_loss(self, stop_price=None):
        """
        Set stop loss for current position

        Args:
            stop_price: Specific stop price, or None to use stop_loss_pct
        """
        if not self.position:
            return

        if stop_price is None:
            stop_price = self.position.close * (1 - self.stop_loss_pct)  # pyright: ignore[reportOperatorIssue]

    def should_stop_out(self) -> bool:
        """
        Check if current position has hit stop loss

        Returns:
            True if stop loss is triggered
        """
        if not self.position:
            return False

        entry_price = self.position.close
        current_price = self.data.Close[-1]
        loss_pct = (entry_price - current_price) / entry_price

        return loss_pct >= self.stop_loss_pct

    def should_take_profit(self) -> bool:
        """
        Check if current position has hit take profit target

        Returns:
            True if take profit is triggered
        """
        if not self.position or self.take_profit_pct is None:
            return False

        entry_price = self.position.close
        current_price = self.data.Close[-1]
        profit_pct = (current_price - entry_price) / entry_price

        return profit_pct >= self.take_profit_pct
