import json
from typing import Any, Dict, List


def load_config() -> Dict[str, Any]:
    """
    Load config file and returns is as a dictionary
    :return: Configuration dictionary
    """
    with open("config.json") as json_data:
        config = json.load(json_data)
        return config
