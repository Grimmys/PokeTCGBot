import pickle

import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button
from pokemontcgsdk import Card

from src.components.paginated_embed import PaginatedEmbed
from src.services.localization_service import LocalizationService
from src.services.settings_service import SettingsService
from src.services.user_service import UserService

SEARCH_PAGE_SIZE = 10


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

    @app_commands.command(name="search", description="Search card with several parameters")
    async def search_command(self, interaction: discord.Interaction, content: str, image_mode: bool = False) -> None:
        user_language_id = self.settings_service.get_user_language_id(
            interaction.user.id)
        all_cards = [{"name": card.id, "value": card.name,
                      "image": card.images.large if card.images.large else card.images.small}
                     for card in Card.where(q=f"name:*{content}*")]

        if len(all_cards) == 0:
            await interaction.response.send_message(
                self.t(user_language_id, 'search_cmd.not_found').replace("{1}", content))
            return

        embed = PaginatedEmbed(all_cards, image_mode, 1 if image_mode else SEARCH_PAGE_SIZE)
        view = View()

        async def change_page_callback(click_interaction: discord.Interaction, forward):
            embed.change_page(forward)
            await interaction.edit_original_response(embed=embed.embed)
            await click_interaction.response.defer()

        next_button = Button(emoji="➡️")
        next_button.callback = lambda click_interaction: change_page_callback(
            click_interaction, True)

        previous_button = Button(emoji="⬅️")
        previous_button.callback = lambda click_interaction: change_page_callback(
            click_interaction, False)

        view.add_item(previous_button)
        view.add_item(next_button)

        await interaction.response.send_message(embed=embed.embed, view=view)

    @app_commands.command(name="collection", description="Search cards in your own collection")
    async def collection_command(self, interaction: discord.Interaction, image_mode: bool = False) -> None:
        user = self.user_service.get_user(interaction.user.id)
        user_language_id = user.settings.language_id

        own_cards = []
        for card_id, quantity in user.cards.items():
            card = self.cards_by_id[card_id]
            entry_card = {
                "name": card.name,
            }
            formatted_id = f"**ID**: {card_id}"
            formatted_quantity = f"**{self.t(user_language_id, 'common.quantity').capitalize()}**: {quantity}"
            if image_mode:
                formatted_rarity = f"**{self.t(user_language_id, 'common.rarity').capitalize()}**: {card.rarity}"
                entry_card["value"] = f"{formatted_id}\n{formatted_rarity}\n{formatted_quantity}"
                entry_card["image"] = card.images.large if card.images.large else card.images.small
            else:
                entry_card["value"] = f"{formatted_id} / {formatted_quantity}"
            own_cards.append(entry_card)

        if len(own_cards) == 0:
            await interaction.response.send_message(
                self.t(user_language_id, 'collection_cmd.empty'))
            return

        embed = PaginatedEmbed(own_cards, image_mode, 1 if image_mode else SEARCH_PAGE_SIZE)
        view = View()

        async def change_page_callback(click_interaction: discord.Interaction, forward):
            embed.change_page(forward)
            await interaction.edit_original_response(embed=embed.embed)
            await click_interaction.response.defer()

        next_button = Button(emoji="➡️")
        next_button.callback = lambda click_interaction: change_page_callback(
            click_interaction, True)

        previous_button = Button(emoji="⬅️")
        previous_button.callback = lambda click_interaction: change_page_callback(
            click_interaction, False)

        view.add_item(previous_button)
        view.add_item(next_button)

        await interaction.response.send_message(embed=embed.embed, view=view)
