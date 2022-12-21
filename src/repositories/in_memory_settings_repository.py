from typing import Optional

from src.repositories.settings_repository import SettingsRepository
from src.entities.user_settings_entity import UserSettingsEntity


class InMemorySettingsRepository(SettingsRepository):
    def __init__(self):
        self._user_settings_entities: list[UserSettingsEntity] = []

    def get_user_settings(self, user_id: int) -> Optional[UserSettingsEntity]:
        for saved_entity in self._user_settings_entities:
            if saved_entity.user_id == user_id:
                return saved_entity
        return None

    def save_user_settings(self, user_settings: UserSettingsEntity) -> bool:
        for index, saved_entity in enumerate(self._user_settings_entities):
            if saved_entity.user_id == user_settings.user_id:
                self._user_settings_entities[index] = user_settings
                return True
        self._user_settings_entities.append(user_settings)
        return True

    def change_user_language(self, user_id: int, new_language_id: int) -> bool:
        for saved_entity in self._user_settings_entities:
            if saved_entity.user_id == user_id:
                saved_entity.language_id = new_language_id
                return True
        return False
