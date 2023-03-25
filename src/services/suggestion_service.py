from typing import Sequence, Optional

import discord

from src.entities.suggestion_entity import SuggestionEntity
from src.repositories.suggestion_repository import SuggestionRepository

MAX_SUGGESTION_CONTENT_SIZE = 1024


class SuggestionService:
    def __init__(self, suggestion_repository: SuggestionRepository):
        self._suggestion_repository = suggestion_repository

    def add_suggestion(self, user: discord.User, suggestion_content: str) -> bool:
        if len(suggestion_content) > MAX_SUGGESTION_CONTENT_SIZE:
            return False
        suggestion = SuggestionEntity(str(user), suggestion_content)
        return self._suggestion_repository.save_suggestion(suggestion)

    def get_all_suggestions(self) -> Sequence[SuggestionEntity]:
        return self._suggestion_repository.get_all()

    def remove_suggestion(self, suggestion_id: str) -> bool:
        return self._suggestion_repository.remove_suggestion(suggestion_id)

    def update_vote_to_suggestion(self, user_id: int, suggestion_id: str, is_positive: bool) -> Optional[SuggestionEntity]:
        if is_positive:
            return self._suggestion_repository.switch_up_vote_for(user_id, suggestion_id)
        else:
            return self._suggestion_repository.switch_down_vote_for(user_id, suggestion_id)
