import pickle
import random

import discord
from discord import Embed, app_commands
from discord.ext import commands
from pokemontcgsdk import Card, Set

from src.services.localization_service import LocalizationService
from src.services.settings_service import SettingsService


class UserInfoCog(commands.Cog):
    def __init__(self, bot: commands.Bot, settings_service: SettingsService,
                 localization_service: LocalizationService) -> None:
        self.bot = bot
        self.settings_service = settings_service
        self.t = localization_service.get_string

    @app_commands.command(name="profile", description="Check your own user profile")
    async def profile_command(self, interaction: discord.Interaction) -> None:
        user_language_id = self.settings_service.get_user_language_id(interaction.user.id)
        emojis = {emoji.name: str(emoji) for emoji in self.bot.emojis}

        embed = Embed(
            title=f"---------- {self.t(user_language_id, 'profile_cmd.title')} ----------",
            color=0xffff00)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)

        embed.add_field(name=f"{self.t(user_language_id, 'common.pokedollar')}s", value=f"{emojis['pokedollar']} 0")
        embed.add_field(name=self.t(user_language_id, 'common.collection').capitalize(), value=f"{emojis['card']} 0")
        embed.add_field(name=f"{self.t(user_language_id, 'common.booster')}s".capitalize(),
                        value=f"{emojis['booster']} 0")

        await interaction.response.send_message(embed=embed)
