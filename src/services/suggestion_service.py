from typing import Sequence

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
