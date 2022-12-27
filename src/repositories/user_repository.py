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
