from typing import Union, Callable, Optional

from discord import Interaction, User, TextStyle
from discord.ui import Button, Modal, TextInput

from src.components.paginated_embed import PaginatedEmbed

_t: Optional[Callable] = None


def setup_class(get_localized_string_method: Callable):
    global _t
    _t = get_localized_string_method


class _NameFilterQueryPopup(Modal, title="Filter by name"):
    name = TextInput(label="Card name", style=TextStyle.short, required=True)

    def __init__(self, related_embed: "SearchCardsEmbed"):
        super().__init__()
        self.related_embed = related_embed
        self.name.label = _t(related_embed.user_language_id, 'search_cards_embed.card_name_input')
        self.title = _t(related_embed.user_language_id, 'search_cards_embed.filter_by_name_label')

    async def on_submit(self, interaction: Interaction):
        await self.related_embed.filter_on_cards_name_action(interaction, self.name.value)
        await interaction.response.defer()


class SearchCardsEmbed(PaginatedEmbed):
    def __init__(self, original_interaction: Interaction, content: list[dict[str, str]], image_mode: bool,
                 user_language_id: int,
                 page_size: int = 1, inline: bool = False, title: str = None, discord_user: User = None,
                 own_cards_filter_disabled=False) -> None:
        super().__init__(original_interaction, content, image_mode, page_size, inline, title, discord_user)
        self.full_content = content
        self.are_owned_cards_displayed = False
        self.user_language_id = user_language_id

        toggle_own_cards_filter_button = Button(emoji="🔮")
        toggle_own_cards_filter_button.callback = lambda click_interaction: self.filter_on_cards_owned_action(
            click_interaction)
        toggle_own_cards_filter_button.disabled = own_cards_filter_disabled
        self.view.add_item(toggle_own_cards_filter_button)

        reset_filters_button = Button(emoji="♻️")
        reset_filters_button.callback = lambda click_interaction: self.reset_filters_action(click_interaction)
        self.view.add_item(reset_filters_button)

        open_name_filter_button = Button(label=_t(user_language_id, 'search_cards_embed.filter_by_name_label'))
        open_name_filter_button.callback = lambda click_interaction: self.open_name_filter_popup(click_interaction)
        self.view.add_item(open_name_filter_button)

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

    async def reset_filters_action(self, interaction: Interaction):
        if interaction.user != self.original_interaction.user:
            return
        self.are_owned_cards_displayed = False
        self.current_page = 0
        self.content = self.full_content
        displayed = self.content[self.current_page * self.page_size:(self.current_page + 1) * self.page_size]
        self.embed.clear_fields()
        self.display_list(displayed)
        await self.original_interaction.edit_original_response(embed=self.embed)
        await interaction.response.defer()

    async def open_name_filter_popup(self, interaction: Interaction):
        if interaction.user != self.original_interaction.user:
            return

        name_filter_popup = _NameFilterQueryPopup(self)

        await interaction.response.send_modal(name_filter_popup)

    async def filter_on_cards_name_action(self, interaction: Interaction, name_input: str):
        if interaction.user != self.original_interaction.user:
            return
        self.current_page = 0
        filter_method = lambda entry_card: self._is_card_matching_name(entry_card, name_input)
        self.content = list(filter(filter_method, self.content))
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

    @staticmethod
    def _is_card_matching_name(entry_card: dict[str, Union[str, int]], name: str) -> bool:
        return name.lower() in entry_card["name"].lower()
