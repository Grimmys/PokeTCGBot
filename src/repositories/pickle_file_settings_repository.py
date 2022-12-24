import pickle
from pathlib import Path
from typing import Optional

from src.entities.user_settings_entity import UserSettingsEntity
from src.repositories.settings_repository import SettingsRepository


class PickleFileSettingsRepository(SettingsRepository):
    PICKLE_FILE_LOCATION = "data/settings.p"

    def __init__(self):
        Path(PickleFileSettingsRepository.PICKLE_FILE_LOCATION).touch(exist_ok=True)

    @staticmethod
    def _load_pickle_file() -> dict[int, UserSettingsEntity]:
        try:
            settings_content = pickle.load(open(PickleFileSettingsRepository.PICKLE_FILE_LOCATION, "rb"))
        except EOFError:
            settings_content = {}
        return settings_content

    @staticmethod
    def _save_pickle_file(content: dict[int, UserSettingsEntity]) -> None:
        pickle.dump(content, open(PickleFileSettingsRepository.PICKLE_FILE_LOCATION, "wb"))

    def get_user_settings(self, user_id: int) -> Optional[UserSettingsEntity]:
        settings_content = PickleFileSettingsRepository._load_pickle_file()
        if user_id in settings_content:
            return settings_content[user_id]
        return None

    def save_user_settings(self, user_settings: UserSettingsEntity) -> bool:
        settings_content = PickleFileSettingsRepository._load_pickle_file()
        settings_content[user_settings.user_id] = user_settings
        PickleFileSettingsRepository._save_pickle_file(settings_content)
        return True

    def change_user_language(self, user_id: int, new_language_id: int) -> bool:
        settings_content = PickleFileSettingsRepository._load_pickle_file()
        if user_id in settings_content:
            settings_content[user_id].language_id = new_language_id
            PickleFileSettingsRepository._save_pickle_file(settings_content)
            return True
        return False
