from typing import Sequence, Callable

from discord import Interaction, User
from discord.ui import Button

from config import BOT_ADMIN_USER_IDS
from src.components.paginated_embed import PaginatedEmbed
from src.utils.types import EntryCard


class CheckSuggestionsEmbed(PaginatedEmbed):
    def __init__(self, original_interaction: Interaction, content: Sequence[EntryCard],
                 user_language_id: int, discord_user: User, remove_suggestion_callback: Callable,
                 title: str = None) -> None:
        super().__init__(original_interaction, content, False, user_language_id, 1, True, title,
                         discord_user)
        self.full_content = content
        self.are_owned_cards_displayed = False
        self.remove_suggestion_callback = remove_suggestion_callback

        remove_suggestion_button = Button(emoji="🗑️")
        remove_suggestion_button.callback = lambda click_interaction: self.remove_active_suggestion(
            click_interaction)
        remove_suggestion_button.disabled = discord_user.id not in BOT_ADMIN_USER_IDS
        self.view.add_item(remove_suggestion_button)

    async def remove_active_suggestion(self, interaction: Interaction) -> None:
        suggestion = self.content[self.current_page]["suggestion"]
        self.remove_suggestion_callback(suggestion.id)
        await interaction.response.send_message(
            PaginatedEmbed._t(self.user_language_id, 'suggestions_embed.suggestion_deleted'),
            delete_after=2)
