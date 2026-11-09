
import json
from copy import deepcopy

from config import CONFIG_PATH, DEFAULT_CONFIG


def load_config():

    CONFIG_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if not CONFIG_PATH.exists():
        save_config(DEFAULT_CONFIG)
        return deepcopy(DEFAULT_CONFIG)

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as file:
            loaded = json.load(file)

        config = deepcopy(DEFAULT_CONFIG)

        def update(target, source):
            for key, value in source.items():
                if isinstance(value, dict) and isinstance(
                    target.get(key), dict
                ):
                    update(target[key], value)
                else:
                    target[key] = value

        update(config, loaded)

        return config

    except (json.JSONDecodeError, OSError):
        return deepcopy(DEFAULT_CONFIG)


def save_config(config):

    CONFIG_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(CONFIG_PATH, "w", encoding="utf-8") as file:
        json.dump(
            config,
            file,
            indent=4,
            ensure_ascii=False
        )
