from typing import List

# Alternative ways of sending required arguments to the application if env variables is not an option for your
# deployment

DISCORD_TOKEN = None

# Required config parameters to replace

# -- Gameplay balancing related
UNCOMMON_UPGRADE_RATE: float = 4.5
DEFAULT_BASIC_BOOSTER_COOLDOWN: int = 10
DEFAULT_PROMO_BOOSTER_COOLDOWN: int = 15
DEFAULT_GRADING_COOLDOWN: int = 40
DAILY_MONEY_GIFT_AMOUNT: int = 5000
BOOSTERS_PRICE: dict[str, int] = {
    "Basic": 100,
    "Promo": 100
}
# -- Discord related
LOG_CHANNEL_ID: int = 0.01
BOT_ADMIN_USER_IDS: List[int] = []