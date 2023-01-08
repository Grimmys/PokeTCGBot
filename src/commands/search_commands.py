import pickle
from typing import Literal

import discord
from discord import app_commands, Embed
from discord.ext import commands
from discord.ui import View, Button
from pokemontcgsdk import Card, PokemonTcgException

from src.colors import ORANGE
from src.components.paginated_embed import PaginatedEmbed
from src.services.localization_service import LocalizationService
from src.services.settings_service import SettingsService
from src.services.user_service import UserService

SEARCH_PAGE_SIZE = 10
NO_RESULT_VALUE = ""


class SearchCog(commands.Cog):
    CARDS_PICKLE_FILE_LOCATION = "data/cards.p"

    def __init__(self, bot: commands.Bot, settings_service: SettingsService,
                 localization_service: LocalizationService, user_service: UserService) -> None:
        self.bot = bot
        self.settings_service = settings_service
        self.t = localization_service.get_string
        self.user_service = user_service
        self.cards_by_id = SearchCog._compute_all_cards()

    @staticmethod
    def _compute_all_cards() -> dict[str, Card]:
        cards: list[Card] = pickle.load(open(SearchCog.CARDS_PICKLE_FILE_LOCATION, "rb"))
        return {card.id: card for card in cards}

    @app_commands.command(name="card", description="Get a card with its id")
    async def get_card_command(self, interaction: discord.Interaction, card_id: str) -> None:
        user_language_id = self.settings_service.get_user_language_id(interaction.user)
        try:
            card = Card.find(card_id)
            formatted_card = self._format_card_for_embed(card, True, user_language_id)
            embed = Embed(title=formatted_card["name"], description=formatted_card["value"], color=ORANGE)
            embed.set_image(url=card.images.large if card.images.large else card.images.small)
            await interaction.response.send_message(embed=embed)
        except PokemonTcgException:
            await interaction.response.send_message(
                self.t(user_language_id, 'get_card_cmd.card_not_found').replace("{1}", card_id))

    @app_commands.command(name="search", description="Search card with several parameters")
    async def search_command(self, interaction: discord.Interaction, content: str,
                             search_mode: Literal["card_name", "card_id", "set_name", "set_id", "rarity"] = "card_name",
                             with_image: bool = False) -> None:
        user_language_id = self.settings_service.get_user_language_id(
            interaction.user)

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

        all_cards = [self._format_card_for_embed(card, with_image, user_language_id)
                     for card in self.cards_by_id.values() if content.lower() in get_search_attribute(card).lower()]

        if len(all_cards) == 0:
            await interaction.response.send_message(
                self.t(user_language_id, 'search_cmd.not_found').replace("{1}", content))
            return

        paginated_embed = PaginatedEmbed(all_cards, with_image, 1 if with_image else SEARCH_PAGE_SIZE)
        view = View()

        async def change_page_callback(click_interaction: discord.Interaction, forward):
            if click_interaction.user != interaction.user:
                return
            paginated_embed.change_page(forward)
            await interaction.edit_original_response(embed=paginated_embed.embed)
            await click_interaction.response.defer()

        next_button = Button(emoji="➡️")
        next_button.callback = lambda click_interaction: change_page_callback(
            click_interaction, True)

        previous_button = Button(emoji="⬅️")
        previous_button.callback = lambda click_interaction: change_page_callback(
            click_interaction, False)

        view.add_item(previous_button)
        view.add_item(next_button)

        await interaction.response.send_message(embed=paginated_embed.embed, view=view)

    @app_commands.command(name="collection", description="Search cards in your own collection")
    async def collection_command(self, interaction: discord.Interaction, with_image: bool = False,
                                 member: discord.User = None) -> None:
        user = self.user_service.get_and_update_user(interaction.user)
        discord_user = interaction.user
        user_language_id = user.settings.language_id

        if member is not None:
            user = self.user_service.get_user(member)
            discord_user = member

            if user is None:
                await interaction.response.send_message(self.t(user_language_id, 'common.user_not_found'))

        own_cards = []
        for card_id, quantity in user.cards.items():
            card = self.cards_by_id[card_id]
            own_cards.append(self._format_card_for_embed(card, with_image, user_language_id, quantity))

        if len(own_cards) == 0:
            await interaction.response.send_message(
                self.t(user_language_id, 'collection_cmd.empty'))
            return

        paginated_embed = PaginatedEmbed(own_cards, with_image, 1 if with_image else SEARCH_PAGE_SIZE,
                               title=f"---------- {self.t(user_language_id, 'collection_cmd.title')} ----------",
                               discord_user=discord_user)
        view = View()

        async def change_page_callback(click_interaction: discord.Interaction, forward):
            if click_interaction.user != interaction.user:
                return
            paginated_embed.change_page(forward)
            await interaction.edit_original_response(embed=paginated_embed.embed)
            await click_interaction.response.defer()

        next_button = Button(emoji="➡️")
        next_button.callback = lambda click_interaction: change_page_callback(
            click_interaction, True)

        previous_button = Button(emoji="⬅️")
        previous_button.callback = lambda click_interaction: change_page_callback(
            click_interaction, False)

        view.add_item(previous_button)
        view.add_item(next_button)

        await interaction.response.send_message(embed=paginated_embed.embed, view=view)

    def _format_card_for_embed(self, card: Card, with_image: bool, user_language_id: int, quantity: int = None):
        entry_card = {
            "name": card.name,
        }
        formatted_id = f"**ID**: {card.id}"
        formatted_rarity = f"**{self.t(user_language_id, 'common.rarity').capitalize()}**: {card.rarity}"
        formatted_set = f"**{self.t(user_language_id, 'common.set').capitalize()}**: {card.set.name} ({card.set.series})"
        formatted_quantity = f"**{self.t(user_language_id, 'common.quantity').capitalize()}**: {quantity}"
        if with_image:
            entry_card["value"] = f"{formatted_id}\n{formatted_rarity}\n{formatted_set}"
            if quantity is not None:
                entry_card["value"] += f"\n{formatted_quantity}"
            entry_card["image"] = card.images.large if card.images.large else card.images.small
        else:
            entry_card["value"] = f"{formatted_id} / {formatted_rarity} / {formatted_set}"
            if quantity is not None:
                entry_card["value"] += f" / {formatted_quantity}"
        return entry_card
