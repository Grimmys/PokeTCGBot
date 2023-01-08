from src.entities.user_cooldowns_entity import UserCooldownsEntity
from src.entities.user_settings_entity import UserSettingsEntity


class UserEntity:
    def __init__(self, user_id: int, name_tag: str = "", money: int = 0, boosters_quantity: int = 0,
                 cards_by_id: dict[str, int] = None, user_settings_entity: UserSettingsEntity = None,
                 user_cooldowns_entity=None):
        self.id: int = user_id
        self.name_tag: str = name_tag
        self.money: int = money
        self.boosters_quantity: int = boosters_quantity
        self.cards: dict[str, int] = cards_by_id if cards_by_id is not None else {}
        self.settings = user_settings_entity if user_settings_entity is not None else UserSettingsEntity()
        self.cooldowns = user_cooldowns_entity if user_cooldowns_entity is not None else UserCooldownsEntity()

    def __setstate__(self, state):
        self.id = state.get("id")
        self.name_tag = state.get("name_tag", "")
        self.money = state.get("money", 0)
        self.boosters_quantity = state.get("boosters_quantity", 0)
        self.cards = state.get("cards", {})
        self.settings = state.get("settings", UserSettingsEntity())
        self.cooldowns = state.get("cooldowns", UserCooldownsEntity())
