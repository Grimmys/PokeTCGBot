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
    def switch_up_vote_for(self, user_id: int, suggestion_id: str) -> SuggestionEntity:
        pass

    @abstractmethod
    def switch_down_vote_for(self, user_id: int, suggestion_id: str) -> SuggestionEntity:
        pass
