from typing import Optional, Sequence

from src.entities.user_entity import UserEntity
from src.repositories.user_repository import UserRepository
from src.utils.card_grade import CardGrade


class InMemoryUserRepository(UserRepository):

    def __init__(self):
        self._user_entities_by_id: dict[int, UserEntity] = {}

    def get_all(self) -> Sequence[UserEntity]:
        return list(self._user_entities_by_id.values())

    def get_user(self, user_id: int) -> Optional[UserEntity]:
        if user_id in self._user_entities_by_id:
            return self._user_entities_by_id[user_id]
        return None

    def save_user(self, user: UserEntity) -> bool:
        self._user_entities_by_id[user.id] = user
        return True

    def change_money(self, user_id: int, money_change: int) -> bool:
        # TODO: implementation
        pass

    def change_all_money(self, money_change: int) -> bool:
        # TODO: implementation
        pass

    def change_basic_boosters_quantity(self, user_id: int, quantity: int) -> bool:
        # TODO: implementation
        pass

    def change_all_basic_boosters_quantity(self, quantity: int) -> bool:
        # TODO: implementation
        pass

    def change_promo_boosters_quantity(self, user_id: int, quantity: int) -> bool:
        # TODO: implementation
        pass

    def change_all_promo_boosters_quantity(self, quantity: int) -> bool:
        # TODO: implementation
        pass

    def change_user_language(self, user_id: int, new_language_id: int) -> bool:
        if user_id in self._user_entities_by_id:
            self._user_entities_by_id[user_id].settings.language_id = new_language_id
            return True
        return False

    def change_booster_opening_with_image_by_default(self, user_id, new_booster_opening_with_image_value):
        # TODO: implementation
        pass

    def change_only_use_booster_stock_with_option(self, user_id, new_only_use_booster_stock_with_option_value):
        # TODO: implementation
        pass

    def change_basic_booster_cooldown(self, user_id: int, updated_timestamp_for_cooldown: int) -> bool:
        # TODO: implementation
        pass

    def change_promo_booster_cooldown(self, user_id: int, updated_timestamp_for_cooldown: int) -> bool:
        # TODO: implementation
        pass

    def change_daily_cooldown(self, user_id: int, updated_timestamp_for_cooldown: int) -> bool:
        # TODO: implementation
        pass

    def change_grading_cooldown(self, user_id: int, updated_timestamp_for_cooldown: int) -> bool:
        # TODO: implementation
        pass

    def add_ungraded_cards_to_collection(self, user_id: int, card_ids: list[str]) -> bool:
        # TODO: implementation
        pass

    def add_graded_card_to_collection(self, user_id: int, card_id: str, grade: CardGrade) -> bool:
        # TODO: implementation
        pass

    def remove_ungraded_card_from_collection(self, user_id: int, card_id: str) -> bool:
        # TODO: implementation
        pass

    def remove_ungraded_cards_from_collection(self, user_id: int, card_ids: list[str]) -> bool:
        # TODO: implementation
        pass

    def get_top_users_by_cards(self, number: int) -> list[UserEntity]:
        # TODO: implementation
        pass
