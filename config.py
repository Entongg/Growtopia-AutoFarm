
from pathlib import Path

APP_NAME = "Growtopia AutoFarm"
APP_VERSION = "0.1.0"

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
LOG_DIR = DATA_DIR / "logs"
CONFIG_PATH = DATA_DIR / "config.json"

DEFAULT_CONFIG = {
    "theme": "dark",

    "farm": {
        "punch_interval": 0.5,
        "put_interval": 0.8,
        "cycle_delay": 1.0,
        "minimum_interval": 0.1,

        "character_position": [960, 540],
        "target_position": [1000, 540],
        "put_position": [920, 540]
    },

    "vision": {
        "confidence_threshold": 0.85,
        "capture_region": None,
        "game_template": ""
    },

    "reconnect": {
        "enabled": False,
        "template": "",
        "retry_notification_seconds": 30
    }
}
