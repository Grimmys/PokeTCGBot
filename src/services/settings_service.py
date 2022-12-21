from src.repositories.settings_repository import SettingsRepository
from src.entities.user_settings_entity import UserSettingsEntity


class SettingsService:
    def __init__(self, settings_repository: SettingsRepository):
        self._settings_repository = settings_repository

    def get_user_language_id(self, user_id: int):
        user_settings_entity = self._settings_repository.get_user_settings(user_id)
        if user_settings_entity is None:
            user_settings_entity = UserSettingsEntity(user_id)
            self._settings_repository.save_user_settings(user_settings_entity)
        return user_settings_entity.language_id

    def update_user_language(self, user_id: int, new_language_id: int):
        if self._settings_repository.get_user_settings(user_id) is None:
            initial_user_settings = UserSettingsEntity(user_id, new_language_id)
            self._settings_repository.save_user_settings(initial_user_settings)
        else:
            self._settings_repository.change_user_language(user_id, new_language_id)
