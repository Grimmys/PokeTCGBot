import time
from typing import Literal

import discord
from discord import Embed, app_commands
from discord.ext import commands

from src.services.localization_service import LocalizationService
from src.services.user_service import UserService, DEFAULT_BASIC_BOOSTER_COOLDOWN, DEFAULT_PROMO_BOOSTER_COOLDOWN
from src.colors import YELLOW, BLUE
from src.utils import discord_tools


class ShoppingCog(commands.Cog):
    def __init__(self, bot: commands.Bot, user_service: UserService,
                 localization_service: LocalizationService) -> None:
        self.bot = bot
        self.user_service = user_service
        self.t = localization_service.get_string

    @app_commands.command(name="market_booster", description="Check available boosters with their prices")
    async def market_booster_command(self, interaction: discord.Interaction) -> None:
        user = self.user_service.get_and_update_user(interaction.user)
        user_language_id = user.settings.language_id

        emojis = {emoji.name: str(emoji) for emoji in self.bot.emojis}

        embed = Embed(
            title=f"---------- {self.t(user_language_id, 'market_booster_cmd.title')} ----------",
            color=BLUE)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)

        embed.add_field(name=f"{emojis['booster']} {self.t(user_language_id, 'common.basic_booster')}",
                        value=f"{emojis['pokedollar']} 100", )
        embed.add_field(name=f"{emojis['booster']} {self.t(user_language_id, 'common.promo_booster')}",
                        value=f"{emojis['pokedollar']} 300", )

        await interaction.response.send_message(embed=embed)
