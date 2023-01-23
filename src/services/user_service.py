from datetime import date, datetime, timedelta
import time
from typing import Optional

import discord

from config import DEFAULT_BASIC_BOOSTER_COOLDOWN, DEFAULT_PROMO_BOOSTER_COOLDOWN
from src.entities.user_entity import UserEntity
from src.repositories.user_repository import UserRepository

NUMBER_TOP_USERS = 50


class UserService:
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    @staticmethod
    def _compute_next_midnight():
        return int(datetime.timestamp(datetime.combine(date.today() + timedelta(days=1), datetime.min.time())))

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

    def give_all_money(self, amount: int) -> bool:
        return self._user_repository.change_all_money(amount)

    def give_boosters(self, user_id: int, kind: str, quantity: int) -> bool:
        if kind == "Basic":
            return self._user_repository.change_basic_boosters_quantity(user_id, quantity)
        elif kind == "Promo":
            return self._user_repository.change_promo_boosters_quantity(user_id, quantity)

    def give_all_boosters(self, kind: str, quantity: int) -> bool:
        if kind == "Basic":
            return self._user_repository.change_all_basic_boosters_quantity(quantity)
        elif kind == "Promo":
            return self._user_repository.change_all_promo_boosters_quantity(quantity)

    def consume_booster(self, user_id: int, kind: str) -> bool:
        if kind == "Basic":
            return self._user_repository.change_basic_boosters_quantity(user_id, -1)
        elif kind == "Promo":
            return self._user_repository.change_promo_boosters_quantity(user_id, -1)

    def reset_basic_booster_cooldown(self, user_id: int) -> None:
        self._user_repository.change_basic_booster_cooldown(user_id, int(time.time()) + DEFAULT_BASIC_BOOSTER_COOLDOWN)

    def reset_promo_booster_cooldown(self, user_id: int) -> None:
        self._user_repository.change_promo_booster_cooldown(user_id, int(time.time()) + DEFAULT_PROMO_BOOSTER_COOLDOWN)

    def reset_daily_cooldown(self, user_id: int) -> None:
        self._user_repository.change_daily_cooldown(user_id, self._compute_next_midnight())

    def add_cards_to_collection(self, user_id: int, drawn_cards_ids: list[str]) -> bool:
        return self._user_repository.add_cards_to_collection(user_id, drawn_cards_ids)

    def remove_card_from_collection(self, user_id: int, card_id: str) -> bool:
        return self._user_repository.remove_card_from_collection(user_id, card_id)

    def get_top_users_collection(self) -> list[UserEntity]:
        return self._user_repository.get_top_users_by_cards(NUMBER_TOP_USERS)

    def transfer_cards(self, sender_id: int, receiver_id: int, card_ids_list: list[str]) -> bool:
        if self._user_repository.remove_cards_from_collection(sender_id, card_ids_list):
            self._user_repository.add_cards_to_collection(receiver_id, card_ids_list)
            return True
        return False

    def transfer_money(self, sender_id: int, receiver_id: int, amount: int) -> bool:
        sender = self._user_repository.get_user(sender_id)
        if sender.money < amount:
            return False

        self._user_repository.change_money(sender_id, - amount)
        self._user_repository.change_money(receiver_id, amount)
        return True
