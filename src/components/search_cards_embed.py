from typing import Union

from discord import Interaction, User
from discord.ui import Button

from src.components.paginated_embed import PaginatedEmbed


class SearchCardsEmbed(PaginatedEmbed):
    def __init__(self, original_interaction: Interaction, content: list[dict[str, str]], image_mode: bool,
                 page_size: int = 1, inline: bool = False, title: str = None, discord_user: User = None) -> None:
        super().__init__(original_interaction, content, image_mode, page_size, inline, title, discord_user)
        self.full_content = content
        self.are_owned_cards_displayed = False

        toggle_own_cards_button = Button(emoji="🔮")
        toggle_own_cards_button.callback = lambda click_interaction: self.filter_on_cards_owned_action(
            click_interaction)

        self.view.add_item(toggle_own_cards_button)

    async def filter_on_cards_owned_action(self, interaction: Interaction):
        if interaction.user != self.original_interaction.user:
            return
        self.are_owned_cards_displayed = not self.are_owned_cards_displayed
        self.current_page = 0
        filter_method = self._is_card_owned if self.are_owned_cards_displayed else self._is_not_card_owned
        self.content = list(filter(filter_method, self.full_content))
        displayed = self.content[self.current_page * self.page_size:(self.current_page + 1) * self.page_size]
        self.embed.clear_fields()
        self.display_list(displayed)
        await self.original_interaction.edit_original_response(embed=self.embed)
        await interaction.response.defer()

    @staticmethod
    def _is_card_owned(entry_card: dict[str, Union[str, int]]) -> bool:
        return entry_card["owned_quantity"] > 0

    @staticmethod
    def _is_not_card_owned(entry_card: dict[str, Union[str, int]]) -> bool:
        return not SearchCardsEmbed._is_card_owned(entry_card)
