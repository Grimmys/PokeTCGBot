from typing import Optional, Sequence, Callable

from discord import Interaction, User, TextStyle, SelectOption
from discord.ui import Button, Modal, TextInput, Select

from src.components.paginated_embed import PaginatedEmbed
from src.services.rarity_service import RarityService
from src.utils.card_grade import GRADES
from src.utils.discord_tools import MAX_DISCORD_SELECT_OPTIONS
from src.utils.types import EntryCard


class FilterQueryPopup(Modal, title="TBD"):
    field = TextInput(label="TBD", style=TextStyle.short, required=True)

    def __init__(self, action_on_submit: Callable, title: str, field_name: str):
        super().__init__()
        self.action = action_on_submit
        self.title = title
        self.field.label = field_name

    async def on_submit(self, interaction: Interaction) -> None:
        await self.action(interaction, self.field.value)
        await interaction.response.defer()


class SearchCardsEmbed(PaginatedEmbed):
    _rarity_service = None

    @staticmethod
    def setup_class(rarity_service: RarityService):
        SearchCardsEmbed._rarity_service = rarity_service

    def __init__(self, original_interaction: Interaction, content: Sequence[EntryCard], image_mode: bool,
                 user_language_id: int, page_size: int = 1, inline: bool = False, title: str = None,
                 discord_user: User = None, own_cards_filter_disabled: bool = False,
                 grade_filter_disabled: bool = False) -> None:
        super().__init__(original_interaction, content, image_mode, user_language_id, page_size, inline, title,
                         discord_user, assets_path="altered_cards")
        self.full_content = content
        self.are_owned_cards_displayed = False

        toggle_own_cards_filter_button = Button(emoji="🔮")
        toggle_own_cards_filter_button.callback = lambda click_interaction: self.filter_on_cards_owned_action(
            click_interaction)
        toggle_own_cards_filter_button.disabled = own_cards_filter_disabled
        self.view.add_item(toggle_own_cards_filter_button)

        reset_filters_button = Button(emoji="♻️")
        reset_filters_button.callback = lambda click_interaction: self.reset_filters_action(click_interaction)
        self.view.add_item(reset_filters_button)

        open_name_filter_button = Button(
            label=SearchCardsEmbed._t(user_language_id, 'search_cards_embed.filter_by_name_label'))
        open_name_filter_button.callback = lambda click_interaction: self.open_name_filter_popup(click_interaction)
        self.view.add_item(open_name_filter_button)

        open_set_name_filter_button = Button(
            label=SearchCardsEmbed._t(user_language_id, 'search_cards_embed.filter_by_set_name_label'))
        open_set_name_filter_button.callback = lambda click_interaction: self.open_set_name_filter_popup(
            click_interaction)
        self.view.add_item(open_set_name_filter_button)

        grade_filter_select = Select(
            placeholder=SearchCardsEmbed._t(user_language_id, 'search_cards_embed.filter_by_grade_label'),
            options=[SelectOption(label=SearchCardsEmbed._t(user_language_id, grade.translation_key),
                                  value=grade.in_application_name) for grade in GRADES])
        grade_filter_select.callback = self.filter_on_cards_grade_action
        grade_filter_select.disabled = grade_filter_disabled
        self.view.add_item(grade_filter_select)

        rarity_filter_select = Select(
            placeholder=SearchCardsEmbed._t(user_language_id, 'search_cards_embed.filter_by_rarity_label'),
            options=[SelectOption(label=rarity.upper(),
                                  value=rarity) for rarity in SearchCardsEmbed._rarity_service.get_all_rarity_names()]
                    [:MAX_DISCORD_SELECT_OPTIONS])
        rarity_filter_select.callback = self.filter_on_cards_rarity_action
        self.view.add_item(rarity_filter_select)

    async def _filter_on_criteria_action(self, interaction: Interaction, criteria_matcher: Callable,
                                         input_value: Optional[str] = None) -> None:
        if interaction.user != self.original_interaction.user:
            return
        self.current_page = 0
        input_value = input_value if input_value is not None else interaction.data["values"][0]
        filter_method = lambda entry_card: criteria_matcher(entry_card, input_value)
        self.content = list(filter(filter_method, self.content))
        self.refresh_page()
        await self.original_interaction.edit_original_response(embed=self.embed, attachments=self.attachments)
        await interaction.response.defer()

    async def filter_on_cards_owned_action(self, interaction: Interaction):
        if interaction.user != self.original_interaction.user:
            return
        self.are_owned_cards_displayed = not self.are_owned_cards_displayed
        self.current_page = 0
        filter_method = self._is_card_owned if self.are_owned_cards_displayed else self._is_not_card_owned
        self.content = list(filter(filter_method, self.full_content))
        self.refresh_page()
        await self.original_interaction.edit_original_response(embed=self.embed, attachments=self.attachments)
        await interaction.response.defer()

    async def reset_filters_action(self, interaction: Interaction):
        if interaction.user != self.original_interaction.user:
            return
        self.are_owned_cards_displayed = False
        self.current_page = 0
        self.content = self.full_content
        self.refresh_page()
        await self.original_interaction.edit_original_response(embed=self.embed, attachments=self.attachments)
        await interaction.response.defer()

    async def open_name_filter_popup(self, interaction: Interaction):
        if interaction.user != self.original_interaction.user:
            return
        name_filter_popup = FilterQueryPopup(self.filter_on_card_name_action,
                                             SearchCardsEmbed._t(self.user_language_id,
                                                                 'search_cards_embed.filter_by_name_label'),
                                             SearchCardsEmbed._t(self.user_language_id,
                                                                 'search_cards_embed.card_name_input'))
        await interaction.response.send_modal(name_filter_popup)

    async def filter_on_card_name_action(self, interaction: Interaction, name_input: str):
        await self._filter_on_criteria_action(interaction, self._is_card_matching_name, name_input)

    async def open_set_name_filter_popup(self, interaction: Interaction):
        if interaction.user != self.original_interaction.user:
            return
        set_filter_popup = FilterQueryPopup(self.filter_on_set_name_action,
                                            SearchCardsEmbed._t(self.user_language_id,
                                                                'search_cards_embed.filter_by_set_name_label'),
                                            SearchCardsEmbed._t(self.user_language_id,
                                                                'search_cards_embed.set_name_input'))
        await interaction.response.send_modal(set_filter_popup)

    async def filter_on_set_name_action(self, interaction: Interaction, name_input: str):
        await self._filter_on_criteria_action(interaction, self._is_card_matching_set, name_input)

    async def filter_on_cards_grade_action(self, interaction: Interaction):
        await self._filter_on_criteria_action(interaction, self._is_card_matching_grade)

    async def filter_on_cards_rarity_action(self, interaction: Interaction):
        await self._filter_on_criteria_action(interaction, self._is_card_matching_rarity)
    @staticmethod
    def _is_card_owned(entry_card: EntryCard) -> bool:
        return entry_card["owned_quantity"] > 0

    @staticmethod
    def _is_not_card_owned(entry_card: EntryCard) -> bool:
        return not SearchCardsEmbed._is_card_owned(entry_card)

    @staticmethod
    def _is_card_matching_name(entry_card: EntryCard, name: str) -> bool:
        return name.lower() in entry_card["name"].lower()

    @staticmethod
    def _is_card_matching_set(entry_card: EntryCard, set_name: str) -> bool:
        return set_name.lower() in entry_card["card"].set.name.lower()

    @staticmethod
    def _is_card_matching_grade(entry_card: EntryCard, grade_name: Optional[str]) -> bool:
        if not grade_name:
            return entry_card["grade"] is None
        if entry_card["grade"] is not None:
            return entry_card["grade"].in_application_name == grade_name
        return False

    @staticmethod
    def _is_card_matching_rarity(entry_card: EntryCard, rarity_name: str) -> bool:
        return entry_card["card"].rarity.lower() == rarity_name.lower()
