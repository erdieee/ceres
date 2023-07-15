import logging

from ceres.balances import Balances
from ceres.exchange import ExchangesHandler
from ceres.remote import Telegram
from ceres.spotarbitrage import SpotArbitrage


logger = logging.getLogger(__name__)


class CeresBot:
    def __init__(self, config) -> None:
        self._config = config
        if config["dry"]:
            logger.info("Bot is running in dry mode")
        self.exchangeshandler = ExchangesHandler(self._config)
        self.wallets = Balances(self._config, self.exchangeshandler)
        self.strategy = SpotArbitrage(self._config, self.exchangeshandler)
        self.symbol = self._config.get("symbol")
        base, quote = self.symbol.split("/")
        self.base = base
        self.quote = quote
        self.total_profit = 0
        self.total_trades = 0
        if self._config.get("telegram", None).get("enabled", False):
            self.telegram = Telegram(self._config)

    def main_loop(self):
        # bal = self.exchangeshandler.get_ticker_on_exchanges('BTC/USDT')
        self.wallets.update_balance()
        signal, orders = self.strategy.check_opportunity()
        if not signal:
            return
        if (
            orders.get("profit", {}).get("profit", 0)
            > self._config.get("min_profit", 0)
        ) and (self._is_balance_enough(orders)):
            logger.info(f"Creating orders now: {orders}")
            self._create_orders(orders)

    def _is_balance_enough(self, orders) -> bool:
        for ex, order in orders.get("exchange_orders").items():
            if not self._check_exchange_balance(ex, order):
                logger.warning(
                    f"Not placing orders. {ex} has not enough funds to {order.get('side')} {self.symbol}"
                )
                return False
        return True

    def _check_exchange_balance(self, ex, order):
        if order.get("side") == "sell":
            return self.wallets.check_free_amount(ex, self.base, order.get("amount"))
        if order.get("side") == "sell":
            return self.wallets.check_free_amount(
                ex, self.quote, order.get("amount") * order.get("price")
            )
        return True

    def _create_orders(self, orders):
        msg = ""
        self.total_profit += float(orders["profit"]["profit"])
        self.total_trades += 1
        for ex, order in orders.get("exchange_orders").items():
            logger.info(
                f"Placing {order['type']} {order['side']} order for {order['amount']} {self.symbol} @ {order['price']} on {ex}"
            )
            msg += f"{order['side']} {order['amount']} {self.symbol} @ {order['price']} on {ex} \n"
            # res = self.exchangeHandler.create_order(
            #     exchange, order["type"], order["side"], order["amount"], order["price"]
            # )
        msg += f"\nTotal trades: {self.total_trades}, total profit: {self.total_profit}"
        self.telegram.send_message(msg)
