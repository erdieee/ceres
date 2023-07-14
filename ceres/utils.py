import json
from pathlib import Path
from typing import Any, Dict, List


def load_config() -> Dict[str, Any]:
    """
    Load config file and returns is as a dictionary
    :return: Configuration dictionary
    """
    with open("config.json") as json_data:
        config = json.load(json_data)
        return config


def create_config(file_name: Path) -> None:
    data = {
        "dry": True,
        "dry_balance": 1000,
        "amount": 1000,
        "order_size": 1000,
        "min_profit": 0.01,
        "symbol": "BTC/USDT",
        "exchanges": [
            {"name": "binance", "key": "", "secret": "", "sandbox": False},
            {"name": "bybit", "key": "", "secret": "", "sandbox": False},
            {"name": "kucoin", "key": "", "secret": "", "sandbox": False},
            {"name": "okx", "key": "", "secret": "", "sandbox": False},
        ],
        "telegram": {
            "enabled": False,
            "token": "",
            "chat_id": "",
        },
    }
    with file_name.open(mode="w") as file:
        json.dump(data, file, indent=4)
