from typing import List

# Alternative ways of sending required arguments to the application if env variables is not an option for your
# deployment

DISCORD_TOKEN = None

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
BOT_ADMIN_USER_IDS: List[int] = []
