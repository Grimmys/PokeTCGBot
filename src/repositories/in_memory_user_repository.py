from typing import Optional

from src.entities.user_entity import UserEntity
from src.repositories.user_repository import UserRepository


class InMemoryUserRepository(UserRepository):
    def __init__(self):
        self._user_entities_by_id: dict[int, UserEntity] = {}

    def get_user(self, user_id: int) -> Optional[UserEntity]:
        if user_id in self._user_entities_by_id:
            return self._user_entities_by_id[user_id]
        return None

    def save_user(self, user: UserEntity) -> bool:
        self._user_entities_by_id[user.id] = user
        return True

    def change_user_language(self, user_id: int, new_language_id: int) -> bool:
        if user_id in self._user_entities_by_id:
            self._user_entities_by_id[user_id].settings.language_id = new_language_id
            return True
        return False
