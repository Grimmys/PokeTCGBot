import pickle
from pathlib import Path
from typing import Optional, Sequence

from src.entities.user_entity import UserEntity
from src.repositories.user_repository import UserRepository
from src.utils.card_grade import CardGrade


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

    def get_all(self) -> Sequence[UserEntity]:
        users_by_id = PickleFileUserRepository._load_pickle_file()
        return list(users_by_id.values())

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

    def change_all_money(self, money_change: int) -> bool:
        users_by_id = PickleFileUserRepository._load_pickle_file()
        for user in users_by_id.values():
            user.money += money_change
        PickleFileUserRepository._save_pickle_file(users_by_id)
        return True

    def change_basic_boosters_quantity(self, user_id: int, quantity: int) -> bool:
        users_by_id = PickleFileUserRepository._load_pickle_file()
        if user_id in users_by_id:
            users_by_id[user_id].boosters_quantity += quantity
            PickleFileUserRepository._save_pickle_file(users_by_id)
            return True
        return False

    def change_all_basic_boosters_quantity(self, quantity: int) -> bool:
        users_by_id = PickleFileUserRepository._load_pickle_file()
        for user in users_by_id.values():
            user.boosters_quantity += quantity
        PickleFileUserRepository._save_pickle_file(users_by_id)
        return True

    def change_promo_boosters_quantity(self, user_id: int, quantity: int) -> bool:
        users_by_id = PickleFileUserRepository._load_pickle_file()
        if user_id in users_by_id:
            users_by_id[user_id].promo_boosters_quantity += quantity
            PickleFileUserRepository._save_pickle_file(users_by_id)
            return True
        return False

    def change_all_promo_boosters_quantity(self, quantity: int) -> bool:
        users_by_id = PickleFileUserRepository._load_pickle_file()
        for user in users_by_id.values():
            user.promo_boosters_quantity += quantity
        PickleFileUserRepository._save_pickle_file(users_by_id)
        return True

    def change_user_language(self, user_id: int, new_language_id: int) -> bool:
        users_by_id = PickleFileUserRepository._load_pickle_file()
        if user_id in users_by_id:
            users_by_id[user_id].settings.language_id = new_language_id
            PickleFileUserRepository._save_pickle_file(users_by_id)
            return True
        return False

    def change_booster_opening_with_image_by_default(self, user_id, new_booster_opening_with_image_value):
        users_by_id = PickleFileUserRepository._load_pickle_file()
        if user_id in users_by_id:
            users_by_id[user_id].settings.booster_opening_with_image = new_booster_opening_with_image_value
            PickleFileUserRepository._save_pickle_file(users_by_id)
            return True
        return False

    def change_only_use_booster_stock_with_option(self, user_id, new_only_use_booster_stock_with_option_value):
        users_by_id = PickleFileUserRepository._load_pickle_file()
        if user_id in users_by_id:
            users_by_id[
                user_id].settings.only_use_booster_stock_with_option = new_only_use_booster_stock_with_option_value
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

    def change_daily_cooldown(self, user_id: int, updated_timestamp_for_cooldown: int) -> bool:
        users_by_id = PickleFileUserRepository._load_pickle_file()
        if user_id in users_by_id:
            users_by_id[user_id].cooldowns.timestamp_for_next_daily = updated_timestamp_for_cooldown
            PickleFileUserRepository._save_pickle_file(users_by_id)
            return True
        return False

    def change_grading_cooldown(self, user_id: int, updated_timestamp_for_cooldown: int) -> bool:
        users_by_id = PickleFileUserRepository._load_pickle_file()
        if user_id in users_by_id:
            users_by_id[user_id].cooldowns.timestamp_for_next_grading = updated_timestamp_for_cooldown
            PickleFileUserRepository._save_pickle_file(users_by_id)
            return True
        return False

    def add_cards_to_collection(self, user_id: int, card_ids: list[str]) -> bool:
        users_by_id = PickleFileUserRepository._load_pickle_file()
        if user_id in users_by_id:
            user = users_by_id[user_id]
            for card_id in card_ids:
                if card_id in user.cards:
                    user.cards[card_id] += 1
                else:
                    user.cards[card_id] = 1
            PickleFileUserRepository._save_pickle_file(users_by_id)
            return True
        return False

    def add_graded_card_to_collection(self, user_id: int, card_id: str, grade: CardGrade) -> bool:
        users_by_id = PickleFileUserRepository._load_pickle_file()
        if user_id in users_by_id:
            user = users_by_id[user_id]
            if (card_id, grade.in_application_name) in user.graded_cards:
                user.graded_cards[(card_id, grade.in_application_name)] += 1
            else:
                user.graded_cards[(card_id, grade.in_application_name)] = 1
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

    def remove_cards_from_collection(self, user_id: int, card_ids: list[str]) -> bool:
        users_by_id = PickleFileUserRepository._load_pickle_file()
        if user_id in users_by_id:
            user = users_by_id[user_id]
            for card_id in card_ids:
                if card_id in user.cards:
                    user.cards[card_id] -= 1
                    if user.cards[card_id] == 0:
                        del user.cards[card_id]
                else:
                    return False
            PickleFileUserRepository._save_pickle_file(users_by_id)
            return True
        return False

    def get_top_users_by_cards(self, number: int) -> list[UserEntity]:
        users_by_id = PickleFileUserRepository._load_pickle_file()
        users: list[UserEntity] = list(users_by_id.values())
        users.sort(key=lambda user: len(user.cards), reverse=True)
        return users[:number]
