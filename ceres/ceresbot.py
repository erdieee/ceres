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
        if self._config.get("telegram", None).get("enabled", False):
            self.telegram = Telegram(self._config)

    def main_loop(self):
        # bal = self.exchangeshandler.get_ticker_on_exchanges('BTC/USDT')
        # logger.info(bal)
        signal, orders = self.strategy.check_opportunity()
        if not signal:
            return
        logger.info(f"Creating orders now: {orders}")
        self.telegram.send_message(orders)
        self.create_orders(orders)

    def create_orders(self, orders):
        pass
