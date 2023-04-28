# Ceres Arbitrage Bot

Check orderbooks asynchronely on different exchanges and search for arbitrage opportunities. No trading direction, no gambling, only taking advantage of market inefficiency.

## Installation

```bash
git clone https://github.com/erdieee/ceres.git

# Enter downloaded directory
cd myodds
pip install -r requirements.txt
pip install -e .
```

Check the cli options with 
```bash
ceres --help
```

To start the bot run
Check the cli options with 
```bash
ceres trade
```

## Configuration

Create a config.json file in the root directory with the following information:

```
{
    "dry": true,
    "dry_balance": 1000,
    "amount": 1000,
    "order_size": 0.01,
    "symbol": "BTC/USDT",
    "exchanges": [
        {
            "name": "binance",
            "key": "",
            "secret": "",
            "sandbox": false
        },
        {
            "name": "bybit",
            "key": "",
            "secret": "",
            "sandbox": false
        },
        {
            "name": "kucoin",
            "key": "",
            "secret": "",
            "sandbox": false
        },
        {
            "name": "okx",
            "key": "",
            "secret": "",
            "sandbox": false
        }
    ],
    "telegram": {
        "enabled": false,
        "token": "",
        "chat_id": ""
    }
}
```