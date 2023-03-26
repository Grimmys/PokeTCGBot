from enum import Enum, auto


class BadgeCategory(Enum):
    GENERAL = auto()
    COLLECTION = auto()
    ACTION = auto()
    EVENT = auto()


class BadgeEntity:
    def __init__(self, badge_id: int, emoji: str, category: BadgeCategory, localization_key: str):
        self.id: int = badge_id
        self.emoji = emoji
        self.category = category
        self.localization_key = localization_key

    def __setstate__(self, state):
        self.id = state.get("id", 0)
        self.emoji = state.get("emoji")
        self.category = state.get("category")
        self.localization_key = state.get("localization_key")
