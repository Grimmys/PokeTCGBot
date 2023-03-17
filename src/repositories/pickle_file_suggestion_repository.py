import pickle
from pathlib import Path
from typing import Sequence

from src.entities.suggestion_entity import SuggestionEntity
from src.repositories.suggestion_repository import SuggestionRepository


class PickleFileSuggestionRepository(SuggestionRepository):
    PICKLE_FILE_LOCATION = "data/suggestions.p"

    def __init__(self):
        Path(PickleFileSuggestionRepository.PICKLE_FILE_LOCATION).touch(exist_ok=True)

    @staticmethod
    def _load_pickle_file() -> list[SuggestionEntity]:
        try:
            suggestions = pickle.load(open(PickleFileSuggestionRepository.PICKLE_FILE_LOCATION, "rb"))
        except EOFError:
            suggestions = []
        return suggestions

    @staticmethod
    def _save_pickle_file(content: Sequence[SuggestionEntity]) -> None:
        pickle.dump(content, open(PickleFileSuggestionRepository.PICKLE_FILE_LOCATION, "wb"))

    def get_all(self) -> Sequence[SuggestionEntity]:
        return PickleFileSuggestionRepository._load_pickle_file()

    def save_suggestion(self, suggestion: SuggestionEntity) -> bool:
        suggestions = PickleFileSuggestionRepository._load_pickle_file()
        suggestions.append(suggestion)
        PickleFileSuggestionRepository._save_pickle_file(suggestions)
        return True

    def remove_suggestion(self, suggestion_id: str) -> bool:
        suggestions = PickleFileSuggestionRepository._load_pickle_file()
        filtered_suggestions = list(filter(lambda suggestion: suggestion.id != suggestion_id, suggestions))
        if len(suggestions) == len(filtered_suggestions):
            return False
        PickleFileSuggestionRepository._save_pickle_file(filtered_suggestions)
        return True
