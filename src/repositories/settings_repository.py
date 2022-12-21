from abc import ABC, abstractmethod
from typing import Optional

from src.entities.user_settings_entity import UserSettingsEntity


class SettingsRepository(ABC):

    @abstractmethod
    def get_user_settings(self, user_id: int) -> Optional[UserSettingsEntity]:
        pass

    @abstractmethod
    def save_user_settings(self, user_settings: UserSettingsEntity) -> bool:
        pass

    @abstractmethod
    def change_user_language(self, user_id: int, new_language_id: int) -> bool:
        pass
