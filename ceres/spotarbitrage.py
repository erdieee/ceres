import logging

from ceres.utils import generate_table

logger = logging.getLogger(__name__)


class SpotArbitrage:
    def __init__(self, config, exchangeshandler, dashboard) -> None:
        self._config = config
        self.exchangeshandler = exchangeshandler
        self.dashboard = dashboard
        self.symbol = self._config.get("symbol")
        self.order_size = self._config.get("order_size", 0)
        self.bids = {}
        self.asks = {}
        self.fees = {}
        self._get_fees()

    def _get_fees(self):
        """
        if not dry check for potential other fees if high vip or other
        """
        markets = self.exchangeshandler.get_markets()
        for ex, market in markets.items():
            m = market.get(self.symbol, None)
            if m:
                self.fees[ex] = {
                    "taker": m.get("taker", 0.001),
                    "maker": m.get("maker", 0.001),
                }
        logger.info(f"Fees per exchange: {self.fees}")

    def check_opportunity(self):
        self.get_orderbook_data()
        return self.check_profit()

    def get_orderbook_data(self):
        obs = self.exchangeshandler.watch_order_books(self.symbol)
        current_exchanges = self.exchangeshandler.current_exchanges
        self.dashboard.update(
            "orderbook",
            generate_table(obs, current_exchanges),
            title="Orderbook",
            border_style="green",
        )
        for ex in current_exchanges:
            self.bids[ex] = obs[ex]["bids"][0][0]
            self.asks[ex] = obs[ex]["asks"][0][0]

    def check_profit(self):
        min_ask_ex = min(self.asks, key=self.asks.get)  # type: ignore
        max_bid_ex = max(self.bids, key=self.bids.get)  # type: ignore
        min_ask_price = self.asks[min_ask_ex]
        max_bid_price = self.bids[max_bid_ex]

        min_fee = self.order_size * min_ask_price * self.fees[min_ask_ex]["taker"]
        max_fee = self.order_size * max_bid_price * self.fees[max_bid_ex]["taker"]

        price_profit = max_bid_price - min_ask_price
        profit = (price_profit * self.order_size) - (min_fee) - (max_fee)
        profit_pct = profit / 100
        logger.debug(
            f"{self.symbol}: Profit after fees: {profit}, buy exchange {min_ask_ex} at: {min_ask_price}, sell exchange {max_bid_ex} at: {max_bid_price}"
        )
        self.dashboard.update(
            "profit",
            f"{self.symbol} \nProfit after fees: {profit} \nBuy exchange {min_ask_ex} at: {min_ask_price} \nSell exchange {max_bid_ex} at: {max_bid_price}",
            title="Profit",
            border_style="red",
        )
        if profit > 0:
            orders = self._create_orders(
                min_ask_ex,
                min_ask_price,
                max_bid_ex,
                max_bid_price,
                profit,
                profit_pct,
                min_fee,
                max_fee,
            )
            logger.info(
                f"Found arbitrage opportunity for {self.symbol} between {min_ask_ex} and {max_bid_ex}"
            )
            return True, orders

        return False, {}

    def _create_orders(
        self,
        min_ask_ex,
        min_ask_price,
        max_bid_ex,
        max_bid_price,
        profit,
        profit_pct,
        min_fee,
        max_fee,
    ):
        return {
            "exchange_orders": {
                min_ask_ex: {
                    "symbol": self.symbol,
                    "type": "limit",
                    "side": "buy",
                    "amount": self.order_size,
                    "price": min_ask_price,
                },
                max_bid_ex: {
                    "symbol": self.symbol,
                    "type": "limit",
                    "side": "sell",
                    "amount": self.order_size,
                    "price": max_bid_price,
                },
            },
            "profit": {
                "profit": profit,
                "profit_pct": profit_pct,
                "fees": min_fee + max_fee,
            },
        }
