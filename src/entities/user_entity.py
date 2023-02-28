import time

from src.entities.quest_entity import QuestEntity
from src.entities.user_cooldowns_entity import UserCooldownsEntity
from src.entities.user_settings_entity import UserSettingsEntity
from src.utils.card_grade import GRADES


class UserEntity:
    def __init__(self, user_id: int, name_tag: str = "", last_interaction_date: int = int(time.time()), money: int = 0,
                 boosters_quantity: int = 0, promo_boosters_quantity: int = 0,
                 cards_by_id: dict[str, int] = None,
                 user_settings_entity: UserSettingsEntity = None,
                 user_cooldowns_entity: UserCooldownsEntity = None, daily_quests: list[QuestEntity] = None, next_daily_quests_refresh: int = 0):
        self.id: int = user_id
        self.name_tag: str = name_tag
        self.last_interaction_date: int = last_interaction_date
        self.money: int = money
        self.boosters_quantity: int = boosters_quantity
        self.promo_boosters_quantity: int = promo_boosters_quantity
        self.cards: dict[tuple[str, str], int] = cards_by_id if cards_by_id is not None else {}
        self.settings: UserSettingsEntity = user_settings_entity if user_settings_entity is not None else UserSettingsEntity()
        self.cooldowns: UserCooldownsEntity = user_cooldowns_entity if user_cooldowns_entity is not None else UserCooldownsEntity()
        self.daily_quests: list[QuestEntity] = daily_quests if daily_quests is not None else []
        self.next_daily_quests_refresh: int = next_daily_quests_refresh

    def count_quantity_of_card(self, card_id: str) -> int:
        quantity = 0
        for grade in GRADES:
            if (card_id, grade.in_application_name) in self.cards:
                quantity += self.cards[(card_id, grade.in_application_name)]
        return quantity

    def __setstate__(self, state):
        self.id = state.get("id")
        self.name_tag = state.get("name_tag", "")
        self.last_interaction_date = state.get("last_interaction_date", 0)
        self.money = state.get("money", 0)
        self.boosters_quantity = state.get("boosters_quantity", 0)
        self.promo_boosters_quantity = state.get("promo_boosters_quantity", 0)
        self.cards = state.get("cards", {})
        self.settings = state.get("settings", UserSettingsEntity())
        self.cooldowns = state.get("cooldowns", UserCooldownsEntity())
        self.daily_quests: list[QuestEntity] = state.get("daily_quests", [])
        self.next_daily_quests_refresh: int = state.get("next_daily_quests_refresh", 0)

