import copy
import logging
from typing import NamedTuple


logger = logging.getLogger(__name__)


class Asset(NamedTuple):
    currency: str
    free: float = 0
    used: float = 0
    total: float = 0


class Balances:
    def __init__(self, config, exchangeshandler) -> None:
        self._config = config
        self._exchangeshandler = exchangeshandler
        self._initial_balance = {}
        self.dry: bool = self._config.get("dry", True)
        self._get_initial_balance()
        self._balance = copy.deepcopy(self._initial_balance)

    def _get_initial_balance(self):
        if self.dry:
            """
            example of balance of a exchange
            {'BTC': {'free': 1.0, 'used': 0.0, 'total': 1.0}, 'ETH': {'free': 0.0, 'used': 0.0, 'total': 0.0}}
            """
            bal = {}
            for coin in self._config.get("symbol").split("/"):
                bal[coin] = Asset(
                    currency=coin,
                    free=self._config.get("dry_balance"),
                    used=0,
                    total=self._config.get("dry_balance"),
                )
            for ex in self._exchangeshandler.current_exchanges:
                self._initial_balance[ex] = bal
        else:
            balances = self._exchangeshandler.get_balances()
            for ex, balance in balances.items():
                bal = {}
                for coin, info in balance:
                    bal[coin] = Asset(
                        currency=coin,
                        free=info.get("free", 0),
                        used=info.get("used", 0),
                        total=info.get("total", 0),
                    )
                self._initial_balance[ex] = bal
        logger.info(f"Starting balance: {self._initial_balance}")

    def get_free(self, exchange, currency) -> float:
        return self._balance[exchange][currency].free

    def get_used(self, exchange, currency) -> float:
        return self._balance[exchange][currency].used

    def get_total(self, exchange, currency) -> float:
        return self._balance[exchange][currency].total

    def get_exchanges_total(self, currency):
        total = 0
        for ex in self._exchangeshandler.current_exchanges:
            total += self.get_total(ex, currency)
        return total

    def update_balance(self):
        if self.dry:
            """will need to store in a database"""
            pass
        else:
            self._update_live()

    def _update_live(self):
        balances = self._exchangeshandler.get_balances()
        for ex, balance in balances.items():
            bal = {}
            for coin, info in balance:
                bal[coin] = Asset(
                    currency=coin,
                    free=info.get("free", 0),
                    used=info.get("used", 0),
                    total=info.get("total", 0),
                )
            self._balance[ex] = bal

    def check_free_amount(self, exchange, currency, amount):
        free = self.get_free(exchange, currency)
        return free >= amount
