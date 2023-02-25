from os import environ as env


def is_dev_mode() -> bool:
    return env.get("DEV_MODE") is not None
