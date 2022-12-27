import pickle
import random

import discord
from discord import Embed, app_commands
from discord.ext import commands
from pokemontcgsdk import Card, Set

from src.services.localization_service import LocalizationService
from src.services.rarity_service import RarityService
from src.services.settings_service import SettingsService
from src.colors import GREEN
from src.services.type_service import TypeService


class BoosterCog(commands.Cog):
    CARDS_PICKLE_FILE_LOCATION = "data/cards.p"

    def __init__(self, bot: commands.Bot, settings_service: SettingsService,
                 localization_service: LocalizationService, rarity_service: RarityService,
                 type_service: TypeService) -> None:
        self.bot = bot
        self.settings_service = settings_service
        self.t = localization_service.get_string
        self.rarity_service = rarity_service
        self.type_service = type_service
        self.sets: list[Set] = Set.all()
        self.all_card: list[Card] = BoosterCog.compute_all_cards()

    @staticmethod
    def compute_all_cards() -> list[Card]:
        return pickle.load(open(BoosterCog.CARDS_PICKLE_FILE_LOCATION, "rb"))

    def _get_card_type_display(self, card: Card) -> str:
        if card.types is None or len(card.types) == 0:
            return ""
        return f"[{self.type_service.get_type(card.types[0].lower()).emoji}]"

    @app_commands.command(name="booster", description="Open a random booster")
    async def booster_command(self, interaction: discord.Interaction) -> None:
        user_language_id = self.settings_service.get_user_language_id(interaction.user.id)

        embed = Embed(
            title=f"---------- {self.t(user_language_id, 'booster_cmd.title')} ----------",
            description=self.t(user_language_id, 'booster_cmd.description'),
            color=GREEN)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)

        for _ in range(random.randint(3, 9)):
            drawn_card = random.choice(self.all_card)
            rarity_emoji = "" if (rarity := self.rarity_service.get_rarity(
                drawn_card.rarity.lower())) is None else rarity.emoji
            type_emoji = self._get_card_type_display(drawn_card)
            embed.add_field(name=drawn_card.id,
                            value=f"{drawn_card.name} {type_emoji}\n `{drawn_card.rarity} {rarity_emoji}`\n ~ {drawn_card.set.name} ~")

        await interaction.response.send_message(embed=embed)
