import os
import pickle
import random
from typing import Literal, Optional

import discord
import requests as requests
from PIL import Image, ImageFilter, ImageEnhance
from discord import app_commands, Embed, File
from discord.ext import commands
from pokemontcgsdk import Card, PokemonTcgException

from config import BOT_ADMIN_USER_IDS
from src.colors import ORANGE
from src.components.search_cards_embed import SearchCardsEmbed
from src.entities.user_entity import UserEntity
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
        self.card_quality_filters = {
            "poor": [Image.open("assets/quality_filters/poor_card_1.png"),
                     Image.open("assets/quality_filters/poor_card_2.png")],
            "average": [Image.open("assets/quality_filters/average_card_1.png"),
                        Image.open("assets/quality_filters/average_card_2.png")],
            "good": [Image.open("assets/quality_filters/good_card_1.png"),
                     Image.open("assets/quality_filters/good_card_2.png")],
            "excellent": None
        }

    @staticmethod
    def _format_boolean_option_value(option_value: bool):
        return "✅" if option_value else "❌"

    @staticmethod
    def _compute_all_cards() -> dict[str, Card]:
        cards: list[Card] = pickle.load(open(SearchCog.CARDS_PICKLE_FILE_LOCATION, "rb"))
        return {card.id: card for card in cards}

    @staticmethod
    def _get_quantity_own_by_user(card_id: str, user: UserEntity) -> int:
        if card_id not in user.cards:
            return 0
        return user.cards[card_id]

    def _format_card_for_embed(self, card: Card, with_image: bool, user_language_id: int, quantity: int,
                               owned_flag: bool = False, viewer_quantity: Optional[int] = None):
        entry_card = {
            "card": card,
            "owned_quantity": viewer_quantity if viewer_quantity is not None else quantity,
            "name": card.name,
        }
        formatted_id = f"**ID**: {card.id}"
        formatted_rarity = f"**{self.t(user_language_id, 'common.rarity').capitalize()}**: {card.rarity}"
        formatted_set = f"**{self.t(user_language_id, 'common.set').capitalize()}**: {card.set.name} ({card.set.series})"
        formatted_quantity = f"**{self.t(user_language_id, 'common.quantity').capitalize()}**: {quantity}"

        owned_quantity = entry_card["owned_quantity"]
        owned_value = f"{SearchCog._format_boolean_option_value(True)} ({owned_quantity})" if owned_quantity > 0 else SearchCog._format_boolean_option_value(
            False)
        formatted_own = f"**{self.t(user_language_id, 'common.card_is_owned').capitalize()}**: {owned_value}"

        spliter_chain = "\n" if with_image else " / "

        entry_card["value"] = f"{formatted_id}{spliter_chain}{formatted_rarity}{spliter_chain}{formatted_set}"

        if not owned_flag or viewer_quantity is not None:
            entry_card["value"] += f"{spliter_chain}{formatted_quantity}"
        if owned_flag:
            entry_card["value"] += f"{spliter_chain}{formatted_own}"

        if with_image:
            entry_card["image"] = card.images.large if card.images.large else card.images.small

        return entry_card

    @app_commands.command(name="card", description="Get a card with its id")
    async def get_card_command(self, interaction: discord.Interaction, card_id: str) -> None:
        user = self.user_service.get_and_update_user(interaction.user)
        user_language_id = user.settings.language_id

        try:
            card = Card.find(card_id)
            formatted_card = self._format_card_for_embed(card, True, user_language_id,
                                                         SearchCog._get_quantity_own_by_user(card_id, user),
                                                         owned_flag=True)
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
        user = self.user_service.get_and_update_user(interaction.user)
        user_language_id = user.settings.language_id

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
                                                 SearchCog._get_quantity_own_by_user(card.id, user), owned_flag=True)
                     for card in self.cards_by_id.values() if content.lower() in get_search_attribute(card).lower()]

        if len(all_cards) == 0:
            await interaction.response.send_message(
                self.t(user_language_id, 'search_cmd.not_found').replace("{1}", content))
            return

        paginated_embed = SearchCardsEmbed(interaction, all_cards, with_image, user_language_id,
                                           1 if with_image else SEARCH_PAGE_SIZE)

        await interaction.response.send_message(embed=paginated_embed.embed, view=paginated_embed.view)

    @app_commands.command(name="collection", description="Search cards in your own collection")
    async def collection_command(self, interaction: discord.Interaction, with_image: bool = False,
                                 member: discord.User = None) -> None:
        user = self.user_service.get_and_update_user(interaction.user)
        collection_user = user
        discord_user = interaction.user
        user_language_id = user.settings.language_id
        someone_else_collection = member is not None

        if someone_else_collection:
            collection_user = self.user_service.get_user(member)
            discord_user = member

            if collection_user is None:
                await interaction.response.send_message(self.t(user_language_id, 'common.user_not_found'))

        own_cards = []
        for card_id, quantity in collection_user.cards.items():
            card = self.cards_by_id[card_id]
            viewer_quantity = SearchCog._get_quantity_own_by_user(card_id, user) if someone_else_collection else None
            own_cards.append(self._format_card_for_embed(card, with_image, user_language_id, quantity,
                                                         owned_flag=someone_else_collection,
                                                         viewer_quantity=viewer_quantity))

        if len(own_cards) == 0:
            await interaction.response.send_message(
                self.t(user_language_id, 'collection_cmd.empty'))
            return

        paginated_embed = SearchCardsEmbed(interaction, own_cards, with_image, user_language_id,
                                           1 if with_image else SEARCH_PAGE_SIZE,
                                           title=f"---------- {self.t(user_language_id, 'collection_cmd.title')} ----------",
                                           discord_user=discord_user,
                                           own_cards_filter_disabled=not someone_else_collection)
        await interaction.response.send_message(embed=paginated_embed.embed, view=paginated_embed.view)

    @app_commands.command(name="random_graded_card", description="Generate a card with some alteration")
    async def random_graded_card(self, interaction: discord.Interaction,
                                 quality: Literal["Poor", "Average", "Good", "Excellent"]) -> None:
        user_language_id = self.settings_service.get_user_language_id(interaction.user)
        quality_lower = quality.lower()

        if interaction.user.id not in BOT_ADMIN_USER_IDS:
            await interaction.response.send_message(self.t(user_language_id, 'common.not_allowed'))
            return
        await interaction.response.send_message(self.t(user_language_id, 'common.loading'))

        random_card: Card = random.choice(list(self.cards_by_id.values()))
        original_image_url = random_card.images.large if random_card.images.large else random_card.images.small
        card_name = f"{random_card.id}_{quality_lower}.png"
        altered_image_path = f"assets/altered_cards/{card_name}"
        card_not_already_computed = not os.path.isfile(altered_image_path)

        if card_not_already_computed:
            altered_image = Image.open(requests.get(original_image_url, stream=True).raw)

            possible_attrition_filters = self.card_quality_filters[quality_lower]

            if possible_attrition_filters:
                attrition_filter = random.choice(possible_attrition_filters)\
                    .resize(altered_image.size)\
                    .filter(ImageFilter.GaussianBlur(7))
                altered_image.paste(attrition_filter, mask=attrition_filter)

            altered_image.save(altered_image_path)

        discord_attachment = File(altered_image_path)
        embed = Embed(title=random_card.id)
        embed.add_field(name="Grade", value=quality)
        embed.set_image(url=f"attachment://{card_name}")
        await interaction.edit_original_response(content="", embed=embed, attachments=[discord_attachment])
