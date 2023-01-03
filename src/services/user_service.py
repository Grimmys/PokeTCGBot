import time

from src.entities.user_entity import UserEntity
from src.repositories.user_repository import UserRepository

DEFAULT_BASIC_BOOSTER_COOLDOWN = 60 * 15
DEFAULT_PROMO_BOOSTER_COOLDOWN = 60 * 60


class UserService:
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    def get_user(self, user_id: int) -> UserEntity:
        user_entity = self._user_repository.get_user(user_id)
        if user_entity is None:
            user_entity = UserEntity(user_id)
            self._user_repository.save_user(user_entity)
        return user_entity

    def give_money(self, user_id: int, amount: int) -> bool:
        return self._user_repository.change_money(user_id, amount)

    def reset_basic_booster_cooldown(self, user_id: int) -> None:
        self._user_repository.change_basic_booster_cooldown(user_id, int(time.time()) + DEFAULT_BASIC_BOOSTER_COOLDOWN)

    def reset_promo_booster_cooldown(self, user_id: int) -> None:
        self._user_repository.change_promo_booster_cooldown(user_id, int(time.time()) + DEFAULT_PROMO_BOOSTER_COOLDOWN)

    def add_cards_to_collection(self, user_id: int, drawn_cards: list[str]) -> None:
        self._user_repository.add_cards_to_collection(user_id, drawn_cards)
