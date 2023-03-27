import random
from typing import Literal, Optional

import discord
from discord import app_commands, Embed, File
from discord.ext import commands
from discord.app_commands import locale_str as _T
from pokemontcgsdk import Card, PokemonTcgException

from config import BOT_ADMIN_USER_IDS
from src.colors import ORANGE
from src.components.search_cards_embed import SearchCardsEmbed
from src.services.card_service import CardService
from src.services.localization_service import LocalizationService
from src.services.settings_service import SettingsService
from src.services.user_service import UserService
from src.utils.card_grade import CardGrade, CardGradeEnum, card_grade_from, OBTAINABLE_GRADES
from src.utils.types import EntryCard

SEARCH_PAGE_SIZE = 10
NO_RESULT_VALUE = ""


class SearchCog(commands.Cog):
    def __init__(self, bot: commands.Bot, settings_service: SettingsService,
                 localization_service: LocalizationService, user_service: UserService,
                 card_service: CardService) -> None:
        self.bot = bot
        self.settings_service = settings_service
        self._t = localization_service.get_string
        self.user_service = user_service
        self.card_service = card_service
        self.cards_by_id = self.card_service.get_all_cards_by_id()

    @staticmethod
    def _format_boolean_option_value(option_value: bool):
        return "✅" if option_value else "❌"

    def _format_card_for_embed(self, card: Card, with_image: bool, user_language_id: int, quantity: int,
                               owned_flag: bool = False, viewer_quantity: Optional[int] = None,
                               grade: Optional[CardGrade] = None, should_display_grade=False) -> EntryCard:
        entry_card = {
            "card": card,
            "owned_quantity": viewer_quantity if viewer_quantity is not None else quantity,
            "name": card.name,
            "grade": grade,
        }
        formatted_id = f"**ID**: {card.id}"
        formatted_rarity = f"**{self._t(user_language_id, 'common.rarity').capitalize()}**: {card.rarity}"
        formatted_set = f"**{self._t(user_language_id, 'common.set').capitalize()}**: {card.set.name} ({card.set.series})"
        formatted_quantity = f"**{self._t(user_language_id, 'common.quantity').capitalize()}**: {quantity}"

        owned_quantity = entry_card["owned_quantity"]
        owned_value = f"{SearchCog._format_boolean_option_value(True)} ({owned_quantity})" if owned_quantity > 0 else SearchCog._format_boolean_option_value(
            False)
        formatted_own = f"**{self._t(user_language_id, 'common.card_is_owned').capitalize()}**: {owned_value}"

        spliter_chain = "\n" if with_image else " / "

        entry_card["value"] = f"{formatted_id}"
        if should_display_grade:
            formatted_grade = f"**{self._t(user_language_id, 'common.grade').capitalize()}**: {self._t(user_language_id, grade.translation_key)}"
            entry_card["value"] += f"{spliter_chain}{formatted_grade}"
        entry_card["value"] += f"{spliter_chain}{formatted_rarity}{spliter_chain}{formatted_set}"
        if not owned_flag or viewer_quantity is not None:
            entry_card["value"] += f"{spliter_chain}{formatted_quantity}"
        if owned_flag:
            entry_card["value"] += f"{spliter_chain}{formatted_own}"

        if with_image:
            if grade is not None and grade.in_application_name != "UNGRADED":
                entry_card["image"] = f"{card.id}_{grade.in_application_name.lower()}.png"
            else:
                entry_card["image"] = card.images.large if card.images.large else card.images.small

        return entry_card

    @app_commands.command(name=_T("get_card_cmd-name"), description=_T("get_card_cmd-desc"))
    async def get_card_command(self, interaction: discord.Interaction, card_id: str) -> None:
        user = self.user_service.get_and_update_user(interaction.user, interaction.locale)
        user_language_id = user.settings.language_id

        if user.is_banned:
            await interaction.response.send_message(self._t(user_language_id, 'common.user_banned'))
            return

        try:
            card = Card.find(card_id)
            formatted_card = self._format_card_for_embed(card, True, user_language_id,
                                                         user.count_quantity_of_card(card_id),
                                                         owned_flag=True)
            embed = Embed(title=formatted_card["name"], description=formatted_card["value"], color=ORANGE)
            embed.set_image(url=card.images.large if card.images.large else card.images.small)
            await interaction.response.send_message(embed=embed)
        except PokemonTcgException:
            await interaction.response.send_message(
                self._t(user_language_id, 'get_card_cmd.card_not_found').replace("{1}", card_id))

    @app_commands.command(name=_T("search_cmd-name"), description=_T("search_cmd-desc"))
    async def search_command(self, interaction: discord.Interaction, content: str,
                             search_mode: Literal["card_name", "card_id", "set_name", "set_id", "rarity"] = "card_name",
                             with_image: bool = False) -> None:
        user = self.user_service.get_and_update_user(interaction.user, interaction.locale)
        user_language_id = user.settings.language_id

        if user.is_banned:
            await interaction.response.send_message(self._t(user_language_id, 'common.user_banned'))
            return

        match search_mode:
            case "card_id":
                get_search_attribute = lambda card: card.id
            case "set_name":
                get_search_attribute = lambda card: card.set.name if card.set else NO_RESULT_VALUE
            case "set_id":
                get_search_attribute = lambda card: card.set.id if card.set else NO_RESULT_VALUE
            case "rarity":
                get_search_attribute = lambda card: card.rarity if card.rarity else NO_RESULT_VALUE
            case _:
                get_search_attribute = lambda card: card.name if card.name else NO_RESULT_VALUE

        all_cards = [self._format_card_for_embed(card, with_image, user_language_id,
                                                 user.count_quantity_of_card(card.id), owned_flag=True)
                     for card in self.cards_by_id.values() if content.lower() in get_search_attribute(card).lower()]

        if len(all_cards) == 0:
            await interaction.response.send_message(
                self._t(user_language_id, 'search_cmd.not_found').replace("{1}", content))
            return

        paginated_embed = SearchCardsEmbed(interaction, all_cards, with_image, user_language_id,
                                           1 if with_image else SEARCH_PAGE_SIZE, grade_filter_disabled=True)

        await interaction.response.send_message(embed=paginated_embed.embed, view=paginated_embed.view)

    @app_commands.command(name=_T("collection_cmd-name"), description=_T("collection_cmd-desc"))
    async def collection_command(self, interaction: discord.Interaction, with_image: bool = False,
                                 member: discord.User = None) -> None:
        user = self.user_service.get_and_update_user(interaction.user, interaction.locale)
        collection_user = user
        discord_user = interaction.user
        user_language_id = user.settings.language_id
        someone_else_collection = member is not None

        if user.is_banned:
            await interaction.response.send_message(self._t(user_language_id, 'common.user_banned'))
            return

        if someone_else_collection:
            collection_user = self.user_service.get_user(member)
            discord_user = member

            if collection_user is None:
                await interaction.response.send_message(self._t(user_language_id, 'common.user_not_found'))

        own_cards: list[EntryCard] = []
        for (card_id, grade_name), quantity in collection_user.cards.items():
            card = self.cards_by_id[card_id]
            viewer_quantity = user.count_quantity_of_card(card_id) if someone_else_collection else None
            own_cards.append(self._format_card_for_embed(card, with_image, user_language_id, quantity,
                                                         owned_flag=someone_else_collection,
                                                         viewer_quantity=viewer_quantity,
                                                         grade=card_grade_from(grade_name),
                                                         should_display_grade=True))

        if len(own_cards) == 0:
            await interaction.response.send_message(
                self._t(user_language_id, 'collection_cmd.empty'))
            return

        paginated_embed = SearchCardsEmbed(interaction, own_cards, with_image, user_language_id,
                                           1 if with_image else SEARCH_PAGE_SIZE,
                                           title=f"---------- {self._t(user_language_id, 'collection_cmd.title')} ----------",
                                           discord_user=discord_user,
                                           own_cards_filter_disabled=not someone_else_collection)
        await interaction.response.send_message(embed=paginated_embed.embed, view=paginated_embed.view,
                                                files=paginated_embed.attachments)

    @app_commands.command(name="random_graded_card", description="Generate a card with some alteration")
    async def random_graded_card(self, interaction: discord.Interaction,
                                 quality: CardGradeEnum) -> None:
        user_language_id = self.settings_service.get_user_language_id(interaction.user)
        grade = OBTAINABLE_GRADES[quality.value]

        if interaction.user.id not in BOT_ADMIN_USER_IDS:
            await interaction.response.send_message(self._t(user_language_id, 'common.not_allowed'))
            return
        await interaction.response.send_message(self._t(user_language_id, 'common.loading'))

        random_card: Card = random.choice(list(self.cards_by_id.values()))
        self.card_service.generate_grade_for_card(random_card, grade)

        card_name = f"{random_card.id}_{grade.in_application_name.lower()}.png"
        discord_attachment = File(f"assets/altered_cards/{card_name}")
        embed = Embed(title=random_card.id)
        embed.add_field(name="Grade", value=self._t(user_language_id, grade.translation_key))
        embed.set_image(url=f"attachment://{card_name}")
        await interaction.edit_original_response(content="", embed=embed, attachments=[discord_attachment])
