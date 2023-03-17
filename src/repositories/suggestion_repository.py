from abc import ABC, abstractmethod
from typing import Sequence

from src.entities.suggestion_entity import SuggestionEntity


class SuggestionRepository(ABC):
    @abstractmethod
    def get_all(self) -> Sequence[SuggestionEntity]:
        pass

    @abstractmethod
    def save_suggestion(self, suggestion: SuggestionEntity) -> bool:
        pass

    @abstractmethod
    def remove_suggestion(self, suggestion_id: str) -> bool:
        pass

    @abstractmethod
    def add_up_vote_to(self, user_id: int, suggestion_id: str) -> SuggestionEntity:
        pass

    @abstractmethod
    def add_down_vote_to(self, user_id: int, suggestion_id: str) -> SuggestionEntity:
        pass
