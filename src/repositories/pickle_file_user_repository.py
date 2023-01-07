import pickle
from pathlib import Path
from typing import Optional

from src.entities.user_entity import UserEntity
from src.repositories.user_repository import UserRepository


class PickleFileUserRepository(UserRepository):
    PICKLE_FILE_LOCATION = "data/users.p"

    def __init__(self):
        Path(PickleFileUserRepository.PICKLE_FILE_LOCATION).touch(exist_ok=True)

    @staticmethod
    def _load_pickle_file() -> dict[int, UserEntity]:
        try:
            users_by_id = pickle.load(open(PickleFileUserRepository.PICKLE_FILE_LOCATION, "rb"))
        except EOFError:
            users_by_id = {}
        return users_by_id

    @staticmethod
    def _save_pickle_file(content: dict[int, UserEntity]) -> None:
        pickle.dump(content, open(PickleFileUserRepository.PICKLE_FILE_LOCATION, "wb"))

    def get_user(self, user_id: int) -> Optional[UserEntity]:
        users_by_id = PickleFileUserRepository._load_pickle_file()
        if user_id in users_by_id:
            return users_by_id[user_id]
        return None

    def save_user(self, user: UserEntity) -> bool:
        users_by_id = PickleFileUserRepository._load_pickle_file()
        users_by_id[user.id] = user
        PickleFileUserRepository._save_pickle_file(users_by_id)
        return True

    def change_money(self, user_id: int, money_change: int) -> bool:
        users_by_id = PickleFileUserRepository._load_pickle_file()
        if user_id in users_by_id:
            users_by_id[user_id].money += money_change
            PickleFileUserRepository._save_pickle_file(users_by_id)
            return True
        return False

    def change_user_language(self, user_id: int, new_language_id: int) -> bool:
        users_by_id = PickleFileUserRepository._load_pickle_file()
        if user_id in users_by_id:
            users_by_id[user_id].settings.language_id = new_language_id
            PickleFileUserRepository._save_pickle_file(users_by_id)
            return True
        return False

    def change_basic_booster_cooldown(self, user_id: int, updated_timestamp_for_cooldown: int) -> bool:
        users_by_id = PickleFileUserRepository._load_pickle_file()
        if user_id in users_by_id:
            users_by_id[user_id].cooldowns.timestamp_for_next_basic_booster = updated_timestamp_for_cooldown
            PickleFileUserRepository._save_pickle_file(users_by_id)
            return True
        return False

    def change_promo_booster_cooldown(self, user_id: int, updated_timestamp_for_cooldown: int) -> bool:
        users_by_id = PickleFileUserRepository._load_pickle_file()
        if user_id in users_by_id:
            users_by_id[user_id].cooldowns.timestamp_for_next_promo_booster = updated_timestamp_for_cooldown
            PickleFileUserRepository._save_pickle_file(users_by_id)
            return True
        return False

    def add_cards_to_collection(self, user_id: int, cards_id: list[str]) -> bool:
        users_by_id = PickleFileUserRepository._load_pickle_file()
        if user_id in users_by_id:
            user = users_by_id[user_id]
            for card_id in cards_id:
                if card_id in user.cards:
                    user.cards[card_id] += 1
                else:
                    user.cards[card_id] = 1
            PickleFileUserRepository._save_pickle_file(users_by_id)
            return True
        return False

    def remove_card_from_collection(self, user_id: int, card_id: str) -> bool:
        users_by_id = PickleFileUserRepository._load_pickle_file()
        if user_id in users_by_id:
            user = users_by_id[user_id]
            if card_id in user.cards:
                user.cards[card_id] -= 1
                if user.cards[card_id] == 0:
                    del user.cards[card_id]
                PickleFileUserRepository._save_pickle_file(users_by_id)
                return True
        return False

    def get_top_users_by_cards(self, number: int) -> list[UserEntity]:
        users_by_id = PickleFileUserRepository._load_pickle_file()
        users: list[UserEntity] = list(users_by_id.values())
        users.sort(key=lambda user: len(user.cards), reverse=True)
        return users[:number]
