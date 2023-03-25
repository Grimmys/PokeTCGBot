import time

import discord

from src.entities.user_entity import UserEntity
from src.repositories.user_repository import UserRepository
from src.entities.user_settings_entity import UserSettingsEntity


class SettingsService:
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    def get_user_language_id(self, user: discord.User):
        user_entity = self._user_repository.get_user(user.id)
        if user_entity is None:
            user_entity = UserEntity(user_id=user.id, name_tag=str(user))
            self._user_repository.save_user(user_entity)
        else:
            user_entity.name_tag = str(user)
            user_entity.last_interaction_date = int(time.time())
            self._user_repository.update_user(user_entity)
        return user_entity.settings.language_id

    def update_user_language(self, user_id: int, new_language_id: int):
        if self._user_repository.get_user(user_id) is None:
            initial_user_entity = UserEntity(user_id, user_settings_entity=UserSettingsEntity(new_language_id))
            self._user_repository.save_user(initial_user_entity)
        else:
            self._user_repository.change_user_language(user_id, new_language_id)

    def update_booster_opening_with_image(self, user_id: int, new_booster_opening_with_image_value: bool):
        self._user_repository.change_booster_opening_with_image_by_default(user_id,
                                                                           new_booster_opening_with_image_value)

    def update_only_use_booster_stock_with_option(self, user_id: int, new_only_use_booster_stock_with_option_value: bool):
        self._user_repository.change_only_use_booster_stock_with_option(user_id, new_only_use_booster_stock_with_option_value)
