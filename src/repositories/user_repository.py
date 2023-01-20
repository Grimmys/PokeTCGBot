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
    def change_money(self, user_id: int, money_change: int) -> bool:
        pass

    @abstractmethod
    def change_basic_boosters_quantity(self, user_id: int, quantity: int) -> bool:
        pass

    @abstractmethod
    def change_promo_boosters_quantity(self, user_id: int, quantity: int) -> bool:
        pass

    @abstractmethod
    def change_user_language(self, user_id: int, new_language_id: int) -> bool:
        pass

    @abstractmethod
    def change_booster_opening_with_image_by_default(self, user_id, new_booster_opening_with_image_value):
        pass

    @abstractmethod
    def change_basic_booster_cooldown(self, user_id: int, updated_timestamp_for_cooldown: int) -> bool:
        pass

    @abstractmethod
    def change_promo_booster_cooldown(self, user_id: int, updated_timestamp_for_cooldown: int) -> bool:
        pass

    @abstractmethod
    def change_daily_cooldown(self, user_id: int, updated_timestamp_for_cooldown: int) -> bool:
        pass

    @abstractmethod
    def add_cards_to_collection(self, user_id: int, cards_id: list[str]) -> bool:
        pass

    @abstractmethod
    def remove_card_from_collection(self, user_id: int, card_id: str) -> bool:
        pass

    @abstractmethod
    def get_top_users_by_cards(self, number: int) -> list[UserEntity]:
        pass
