from discord import Interaction, User
from discord.ui import Button

from src.components.paginated_embed import PaginatedEmbed


class SearchCardsEmbed(PaginatedEmbed):
    def __init__(self, original_interaction: Interaction, content: list[dict[str, str]], image_mode: bool,
                 page_size: int = 1, inline: bool = False, title: str = None, discord_user: User = None) -> None:
        super().__init__(original_interaction, content, image_mode, page_size, inline, title, discord_user)
        self.full_content = content

        toggle_own_cards_button = Button(emoji="🔮")
        toggle_own_cards_button.callback = lambda click_interaction: self.filter_on_cards_owned(click_interaction)

        self.view.add_item(toggle_own_cards_button)

    async def filter_on_cards_owned(self, interaction: Interaction):
        if interaction.user != self.original_interaction.user:
            return
        self.current_page = 0
        self.content = list(filter(lambda entry_card: entry_card["owned_quantity"] > 0, self.full_content))
        displayed = self.content[self.current_page * self.page_size:(self.current_page + 1) * self.page_size]
        self.embed.clear_fields()
        self.display_list(displayed)
        await self.original_interaction.edit_original_response(embed=self.embed)
        await interaction.response.defer()
