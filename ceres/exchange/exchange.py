from datetime import datetime
import logging

import ccxt.pro as ccxt

logger = logging.getLogger(__name__)


class Exchange:
    def __init__(self, config, ex_dict={}) -> None:
        self._config = config
        self.dry = self._config.get('dry', True)
        self.ex_dict = ex_dict
        self.api = self.init_exchange(self.ex_dict)

    def init_exchange(self, ex_dict):
        name = ex_dict.get("name")

        ex_config = {
            "apiKey": ex_dict.get("key"),
            "secret": ex_dict.get("secret"),
            "password": ex_dict.get("password"),
        }
        try:
            api = getattr(ccxt, name.lower())(ex_config)
        except ccxt.BaseError as e:
            raise Exception(f"Initialization of ccxt failed. Reason: {e}") from e

        # Sandbox mode need to be set before any call
        self.sandbox_mode(ex_dict, api, name)
        return api

    def sandbox_mode(self, ex_dict, api, name):
        if ex_dict.get("sandbox"):
            if api.urls.get("test"):
                api.set_sandbox_mode(True)
                logger.info(f"Enabled Sandbox API on {name}")
            else:
                logger.warning(f"No Sandbox URL in CCXT for {name}, exiting.")
                raise Exception(f"Exchange {name} does not provide a sandbox api")

    @property
    def name(self):
        return self.api.id

    def __str__(self) -> str:
        return self.api.name

    def __repr__(self) -> str:
        return self.api.name

    async def watch_order_book(self, symbol):
        if self.check_exchange_has("watchOrderBook"):
            return await self.api.watch_order_book(symbol)

    async def watch_ticker(self, symbol):    
        # watch tickers not working fetch ticker for now
        try:
            return await self.api.fetch_ticker(symbol)
        except ccxt.DDoSProtection as e:
            raise Exception(e) from e
        except (ccxt.NetworkError, ccxt.ExchangeError) as e:
            raise Exception(
                f'Could not load ticker due to {e.__class__.__name__}. Message: {e}') from e
        except ccxt.BaseError as e:
            raise Exception(e) from e

    async def load_markets(self, reload=False):
        return await self.api.load_markets(reload=reload)

    async def watch_balance(self):
        try:
            balance = await self.api.fetch_balance()
            balance.pop("info")
            balance.pop("free", None)
            balance.pop("total", None)
            balance.pop("used", None)
            return balance

        except ccxt.DDoSProtection as e:
            raise Exception(e) from e
        except (ccxt.NetworkError, ccxt.ExchangeError) as e:
            raise Exception(f'Could not get balance due to {e.__class__.__name__}. Message: {e}') from e
        except ccxt.BaseError as e:
            raise Exception(e) from e

    def create_simulated_order(self, symbol, type, side, amount, price, params): 
        # assuming all trades immediately filled
        # still need to consider fees
        
        simulated_order = {'id': f'dry_order_{datetime.utcnow().timestamp()}',
            'datetime': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'timestamp': datetime.utcnow().timestamp(),
            'symbol': symbol,
            'type': type,
            'timeInForce': 'GTC',
            'postOnly': False,
            'side': side,
            'price': price,
            'amount': amount,
            'cost': amount * price,
            'filled': amount,
            'remaining': 0.0,
            'status': 'closed',
            'fee': None,
            'trades': [],
            'info': {},
            'fees': [],
            'reduceOnly': None}

        return simulated_order

    async def create_order(self, *, symbol, type, side, amount, price, params):
        if self.dry:
            order = self.create_simulated_order(symbol, type, side, amount, price, params)
            return order

        try:
            order = await self.api.create_order(
                symbol,
                type,
                side,
                amount,
                price,
                params
            )
            return order
        except ccxt.InsufficientFunds as e:
            logger.warning(
                f'Insufficient funds to create {type} {side} order on market {symbol}. '
                f'Tried to {side} amount {amount} at rate {price}.'
                f'Message: {e}')
        except ccxt.InvalidOrder as e:
            logger.warning(
                f'Could not create {type} {side} order on market {symbol}. '
                f'Tried to {side} amount {amount} at rate {price}. '
                f'Message: {e}') 
        except ccxt.DDoSProtection as e:
            logger.warning(e)
        except (ccxt.NetworkError, ccxt.ExchangeError) as e:
            logger.warning(
                f'Could not place {side} order due to {e.__class__.__name__}. Message: {e}')
        except ccxt.BaseError as e:
            logger.warning(e)

    def check_exchange_has(self, method=str) -> bool:
        if self.api.has.get(method, False):
            return True
        raise Exception(f"{self.name} does not support {method}.")
