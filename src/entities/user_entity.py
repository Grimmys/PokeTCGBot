from src.entities.user_cooldowns_entity import UserCooldownsEntity
from src.entities.user_settings_entity import UserSettingsEntity


class UserEntity:
    def __init__(self, user_id: int, money: int = 0, boosters_quantity: int = 0,
                 user_settings_entity: UserSettingsEntity = None, user_cooldowns_entity = None):
        self.id = user_id
        self.money = money
        self.boosters_quantity = boosters_quantity
        self.settings = user_settings_entity if user_settings_entity is not None else UserSettingsEntity()
        self.cooldowns = user_cooldowns_entity if user_cooldowns_entity is not None else UserCooldownsEntity()
