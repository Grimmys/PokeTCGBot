from abc import ABC, abstractmethod
from typing import Optional

from src.entities.user_entity import UserEntity


class UserRepository(ABC):

    @abstractmethod
    def get_user(self, user_id: int) -> Optional[UserEntity]:
        pass

    @abstractmethod
    def save_user(self, user: UserEntity) -> bool:
        pass

    @abstractmethod
    def change_user_language(self, user_id: int, new_language_id: int) -> bool:
        pass

    @abstractmethod
    def change_basic_booster_cooldown(self, user_id: int, updated_timestamp_for_cooldown: int) -> bool:
        pass

    @abstractmethod
    def change_promo_booster_cooldown(self, user_id: int, updated_timestamp_for_cooldown: int) -> bool:
        pass

    @abstractmethod
    def add_cards_to_collection(self, user_id: int, cards_id: list[str]) -> None:
        pass
