from typing import List

# Alternative ways of sending required arguments to the application if env variables is not an option for your
# deployment

DISCORD_TOKEN = "MTA1NDYzNjk1NzI5ODMzMTcwOQ.GV9OD3.m4uIMAc8uNhYcP27lpNmz8yH9FYNarHb2u4MOw"

# Required config parameters to replace

# -- Gameplay balancing related
UNCOMMON_UPGRADE_RATE: float = None
DEFAULT_BASIC_BOOSTER_COOLDOWN: int = None
DEFAULT_PROMO_BOOSTER_COOLDOWN: int = None
DEFAULT_GRADING_COOLDOWN: int = None
DAILY_MONEY_GIFT_AMOUNT: int = None
BOOSTERS_PRICE: dict[str, int] = {
    "Basic": None,
    "Promo": None
}

# -- Discord related
LOG_CHANNEL_ID: int = None
BOT_ADMIN_USER_IDS: List[int] = [381860176677961730]