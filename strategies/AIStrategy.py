import backtrader as bt
import logging


class AIStrategy(bt.Strategy):
    """A dumb bt strategy generated by AI.
    Args:
        It will strictly follow the signal by AI in below manner:
        Buy/sell when get the  signal, and keep the position until the signal changes,
        close the position, and start another Sell/Buy.
    """

    sellAnxietyThreshold = 0
    buyAnxietyThreshold = 0

    def __init__(self):
        # print('init')
        # print("self.data0:")
        # print(self.data0.lines.getlinealiases())
        self.buyAnxiety = 1
        self.sellAnxiety = 1

    def next(self):
        if not self.position and self.data0.signal[0] != 0:
            if self.data0.signal[0] > 0:
                self.sell()
            else:
                self.buy()
        else:
            if self.position.size > 0 and self.data0.signal[0] < 0:
                self.sellAnxiety += 1
                if self.sellAnxiety > self.sellAnxietyThreshold:
                    self.sellAnxiety = 0
                    self.buyAnxiety = 0
                    self.close()
                    self.sell()
            if self.position.size < 0 and self.data0.signal[0] > 0:
                self.buyAnxiety += 1
                if self.buyAnxiety > self.buyAnxietyThreshold:
                    self.buyAnxiety = 0
                    self.sellAnxiety = 0
                    self.close()
                    self.buy()
        return

    def start(self):
        print("Backtesting starts...")

    def stop(self):
        print("Backtesting ends.")

    def log(self, txt, dt=None):
        """Logging function fot this strategy"""
        dt = dt or self.datas[0].datetime.date(0)
        print("%s, %s" % (dt.isoformat(), txt))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return
        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    "BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f"
                    % (order.executed.price, order.executed.value, order.executed.comm)
                )

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log(
                    "SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f"
                    % (order.executed.price, order.executed.value, order.executed.comm)
                )

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log("Order Canceled/Margin/Rejected")

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log("OPERATION PROFIT, GROSS %.2f, NET %.2f" % (trade.pnl, trade.pnlcomm))
