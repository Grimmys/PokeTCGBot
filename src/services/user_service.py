import time

from src.entities.user_entity import UserEntity
from src.repositories.user_repository import UserRepository

DEFAULT_BASIC_BOOSTER_COOLDOWN = 60 * 15
DEFAULT_PROMO_BOOSTER_COOLDOWN = 60 * 30


class UserService:
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    def get_user(self, user_id: int):
        user_entity = self._user_repository.get_user(user_id)
        if user_entity is None:
            user_entity = UserEntity(user_id)
            self._user_repository.save_user(user_entity)
        return user_entity

    def reset_basic_booster_cooldown(self, user_id: int):
        self._user_repository.change_basic_booster_cooldown(user_id, int(time.time()) + DEFAULT_BASIC_BOOSTER_COOLDOWN)
