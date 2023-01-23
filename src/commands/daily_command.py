import time

import discord
from discord import app_commands
from discord.ext import commands

from config import DAILY_MONEY_GIFT_AMOUNT
from src.services.localization_service import LocalizationService
from src.services.user_service import UserService
from src.utils import discord_tools


class DailyCog(commands.Cog):
    def __init__(self, bot: commands.Bot, localization_service: LocalizationService, user_service: UserService) -> None:
        self.bot = bot
        self.t = localization_service.get_string
        self.user_service = user_service

    @app_commands.command(name="daily", description="Claim daily gift")
    async def daily_command(self, interaction: discord.Interaction) -> None:
        user = self.user_service.get_user(interaction.user)
        user_language_id = user.settings.language_id

        if user.cooldowns.timestamp_for_next_daily > time.time():
            discord_formatted_timestamp = discord_tools.timestamp_to_relative_time_format(
                user.cooldowns.timestamp_for_next_daily)
            await interaction.response.send_message(
                f"{self.t(user_language_id, 'common.daily_cooldown')} {discord_formatted_timestamp}")
            return

        self.user_service.reset_daily_cooldown(user.id)
        money_gift_amount = DAILY_MONEY_GIFT_AMOUNT
        self.user_service.give_money(user.id, money_gift_amount)

        await interaction.response.send_message(
            self.t(user_language_id, 'daily_cmd.response_msg').format(amount=money_gift_amount))
