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
