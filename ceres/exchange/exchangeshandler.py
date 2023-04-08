import logging
import asyncio

from ceres.exchange import Exchange

logger = logging.getLogger(__name__)


class ExchangesHandler:
    def __init__(self, config) -> None:
        self._config = config
        self.symbol = self._config.get("symbol")
        self.exchanges_list = []
        self.exchanges = {}
        self.markets = {}
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self._get_exchanges()
        self.markets = self._load_markets()
        self._check_symbol_on_exchange()

    def _get_exchanges(self):
        ex_info = self._config.get("exchanges")
        for ex in ex_info:
            name = ex.get("name")
            self.exchanges[name] = Exchange(self._config, ex)
        self.exchanges_list = list(self.exchanges.keys())

    def __del__(self):
        """Destructor - clean up async"""
        self.close()

    def close(self):
        logger.info("ExchangesHandler object destroyed, closing async loop")
        if self.loop and not self.loop.is_closed():
            self.loop.close()

    @property
    def current_exchanges(self):
        return self.exchanges_list

    def get_markets(self):
        if not self.markets:
            self.markets = self._load_markets()
        return self.markets

    async def _gather_tasks(self, operation, params=None):
        if params:
            tasks = [
                getattr(self.exchanges[ex], operation)(params)
                for ex in self.exchanges_list
            ]
        else:
            tasks = [
                getattr(self.exchanges[ex], operation)() for ex in self.exchanges_list
            ]
        return await asyncio.gather(*tasks)

    def watch_order_books(self, params=None):
        return dict(
            zip(
                self.exchanges_list,
                self.loop.run_until_complete(
                    self._gather_tasks(operation="watch_order_book", params=params)
                ),
            )
        )

    def get_balances(self, params=None):
        return dict(
            zip(
                self.exchanges_list,
                self.loop.run_until_complete(
                    self._gather_tasks(operation="watch_balance", params=params)
                ),
            )
        )

    def get_ticker_on_exchanges(self, params=None):
        return dict(
            zip(
                self.exchanges_list,
                self.loop.run_until_complete(
                    self._gather_tasks(operation="watch_ticker", params=params)
                ),
            )
        )

    def _load_markets(self):
        logger.info(f"Loading markets for exchanges {*self.exchanges_list,}")
        return dict(
            zip(
                self.exchanges_list,
                self.loop.run_until_complete(
                    self._gather_tasks(operation="load_markets")
                ),
            )
        )

    def _check_symbol_on_exchange(self):
        for ex, market in self.markets.items():
            if not self.symbol in market:
                raise Exception(
                    f"{ex} does not have market symbol {self.symbol}. Please delete it or check if it is correctly written."
                )
