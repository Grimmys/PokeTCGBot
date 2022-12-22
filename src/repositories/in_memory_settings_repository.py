from typing import Optional

from src.repositories.settings_repository import SettingsRepository
from src.entities.user_settings_entity import UserSettingsEntity


class InMemorySettingsRepository(SettingsRepository):
    def __init__(self):
        self._user_settings_entities_by_id: dict[int, UserSettingsEntity] = {}

    def get_user_settings(self, user_id: int) -> Optional[UserSettingsEntity]:
        if user_id in self._user_settings_entities_by_id:
            return self._user_settings_entities_by_id[user_id]
        return None

    def save_user_settings(self, user_settings: UserSettingsEntity) -> bool:
        self._user_settings_entities_by_id[user_settings.user_id] = user_settings
        return True

    def change_user_language(self, user_id: int, new_language_id: int) -> bool:
        if user_id in self._user_settings_entities_by_id:
            self._user_settings_entities_by_id[user_id].language_id = new_language_id
            return True
        return False
