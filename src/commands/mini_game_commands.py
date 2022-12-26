import random

import discord
from discord import Embed, app_commands
from discord.ext import commands

from src.services.localization_service import LocalizationService
from src.services.settings_service import SettingsService


class MiniGamesCog(commands.Cog):
    NUMBER_OF_JOKES = 20

    def __init__(self, bot: commands.Bot, settings_service: SettingsService,
                 localization_service: LocalizationService) -> None:
        self.bot = bot
        self.settings_service = settings_service
        self.t = localization_service.get_string

    @app_commands.command(name="joke", description="Get a (bad) Pokémon joke")
    async def joke_command(self, interaction: discord.Interaction) -> None:
        user_language_id = self.settings_service.get_user_language_id(interaction.user.id)

        joke_id = f"joke_cmd.joke_{random.randint(1, MiniGamesCog.NUMBER_OF_JOKES)}"

        content = f"_{self.t(user_language_id, 'joke_cmd.description')}_\n\n {self.t(user_language_id, joke_id)}"

        embed = Embed(
            title=f"---------- {self.t(user_language_id, 'joke_cmd.title')} ----------",
            description=content,
            color=0xa020f0)

        await interaction.response.send_message(embed=embed)
