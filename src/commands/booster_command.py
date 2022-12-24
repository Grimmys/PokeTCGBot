import random

import discord
from discord import Embed, app_commands
from discord.ext import commands
from pokemontcgsdk import Card, Set

from src.services.localization_service import LocalizationService
from src.services.settings_service import SettingsService


class BoosterCog(commands.Cog):
    def __init__(self, bot: commands.Bot, settings_service: SettingsService,
                 localization_service: LocalizationService) -> None:
        self.bot = bot
        self.settings_service = settings_service
        self.t = localization_service.get_string
        self.sets: list[Set] = Set.all()
        self.all_card_ids: list[str] = BoosterCog.compute_all_card_ids(self.sets)

    @staticmethod
    def compute_all_card_ids(sets: list[Set]) -> list[str]:
        ids: list[str] = []
        for card_set in sets:
            for index in range(1, card_set.total + 1):
                ids.append(f"{card_set.id}-{index}")
        return ids

    @app_commands.command(name="booster", description="Open a random booster")
    async def booster_command(self, interaction: discord.Interaction) -> None:
        user_language_id = self.settings_service.get_user_language_id(interaction.user.id)

        embed = Embed(
            title=f"---------- {self.t(user_language_id, 'booster_cmd.title')} ----------",
            description=self.t(user_language_id, 'booster_cmd.description'),
            color=0x00ff00)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)

        drawn_card_id = random.choice(self.all_card_ids)
        card = Card.find(drawn_card_id)
        embed.set_image(url=card.images.large if card.images.large else card.images.small)

        await interaction.response.send_message(embed=embed)
