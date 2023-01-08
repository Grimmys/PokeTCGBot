import time
from typing import Optional

import discord

from src.entities.user_entity import UserEntity
from src.repositories.user_repository import UserRepository

DEFAULT_BASIC_BOOSTER_COOLDOWN = 60 * 15
DEFAULT_PROMO_BOOSTER_COOLDOWN = 60 * 60

NUMBER_TOP_USERS = 50


class UserService:
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    def get_user(self, user: discord.User) -> Optional[UserEntity]:
        return self._user_repository.get_user(user.id)

    def get_and_update_user(self, user: discord.User) -> UserEntity:
        user_entity = self._user_repository.get_user(user.id)
        if user_entity is None:
            user_entity = UserEntity(user_id=user.id, name_tag=str(user))
            self._user_repository.save_user(user_entity)
        else:
            user_entity.last_interaction_date = int(time.time())
            user_entity.name_tag = str(user)
            self._user_repository.save_user(user_entity)
        return user_entity

    def give_money(self, user_id: int, amount: int) -> bool:
        return self._user_repository.change_money(user_id, amount)

    def reset_basic_booster_cooldown(self, user_id: int) -> None:
        self._user_repository.change_basic_booster_cooldown(user_id, int(time.time()) + DEFAULT_BASIC_BOOSTER_COOLDOWN)

    def reset_promo_booster_cooldown(self, user_id: int) -> None:
        self._user_repository.change_promo_booster_cooldown(user_id, int(time.time()) + DEFAULT_PROMO_BOOSTER_COOLDOWN)

    def add_cards_to_collection(self, user_id: int, drawn_cards_ids: list[str]) -> bool:
        return self._user_repository.add_cards_to_collection(user_id, drawn_cards_ids)

    def remove_card_from_collection(self, user_id: int, card_id: str) -> bool:
        return self._user_repository.remove_card_from_collection(user_id, card_id)

    def get_top_users_collection(self) -> list[UserEntity]:
        return self._user_repository.get_top_users_by_cards(NUMBER_TOP_USERS)
