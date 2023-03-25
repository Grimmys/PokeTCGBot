from typing import Sequence, Callable

from discord import Interaction, User
from discord.ui import Button

from config import BOT_ADMIN_USER_IDS
from src.components.paginated_embed import PaginatedEmbed
from src.utils.types import EntryCard


class CheckSuggestionsEmbed(PaginatedEmbed):
    def __init__(self, original_interaction: Interaction, content: Sequence[EntryCard],
                 user_language_id: int, discord_user: User, update_vote_callback: Callable,
                 remove_suggestion_callback: Callable, title: str = None) -> None:
        super().__init__(original_interaction, content, False, user_language_id, 1, False, title,
                         discord_user)
        self.user = discord_user
        self.full_content = content
        self.update_vote_callback = update_vote_callback
        self.remove_suggestion_callback = remove_suggestion_callback

        add_up_vote_button = Button(emoji="👍")
        add_up_vote_button.callback = lambda click_interaction: self.up_vote_active_suggestion(
            click_interaction)
        self.view.add_item(add_up_vote_button)

        add_down_vote_button = Button(emoji="👎")
        add_down_vote_button.callback = lambda click_interaction: self.down_vote_active_suggestion(
            click_interaction)
        self.view.add_item(add_down_vote_button)

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

    async def up_vote_active_suggestion(self, interaction: Interaction) -> None:
        active_element = self.content[self.current_page]
        optional_suggestion = self.update_vote_callback(self.user.id, active_element["suggestion"].id, True)
        if optional_suggestion is None:
            await interaction.response.send_message(
                PaginatedEmbed._t(self.user_language_id, 'suggestions_embed.upvote_downvoted_suggestion_error'),
                delete_after=2)
            return
        active_element["suggestion"] = optional_suggestion
        self.refresh_page()
        await self.original_interaction.edit_original_response(embed=self.embed)
        await interaction.response.send_message(
            PaginatedEmbed._t(self.user_language_id, 'suggestions_embed.suggestion_up_voted'),
            delete_after=2)

    async def down_vote_active_suggestion(self, interaction: Interaction) -> None:
        active_element = self.content[self.current_page]
        optional_suggestion = self.update_vote_callback(self.user.id, active_element["suggestion"].id, False)
        if optional_suggestion is None:
            await interaction.response.send_message(
                PaginatedEmbed._t(self.user_language_id, 'suggestions_embed.downvote_upvoted_suggestion_error'),
                delete_after=2)
            return
        active_element["suggestion"] = optional_suggestion
        self.refresh_page()
        await self.original_interaction.edit_original_response(embed=self.embed)
        await interaction.response.send_message(
            PaginatedEmbed._t(self.user_language_id, 'suggestions_embed.suggestion_down_voted'),
            delete_after=2)

    def display_element(self, element: dict[str, any]) -> None:
        super().display_element(element)
        self.embed.add_field(
            name=PaginatedEmbed._t(self.user_language_id, 'suggestions_embed.up_votes'),
            value=element["suggestion"].count_up_votes(), inline=True)
        self.embed.add_field(
            name=PaginatedEmbed._t(self.user_language_id, 'suggestions_embed.down_votes'),
            value=element["suggestion"].count_down_votes(), inline=True)
