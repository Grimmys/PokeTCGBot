import time

import discord
from discord import Embed, app_commands
from discord.ext import commands

from src.services.localization_service import LocalizationService
from src.services.user_service import UserService, DEFAULT_BASIC_BOOSTER_COOLDOWN, DEFAULT_PROMO_BOOSTER_COOLDOWN
from src.colors import YELLOW
from src.utils import discord_tools


class UserInfoCog(commands.Cog):
    def __init__(self, bot: commands.Bot, user_service: UserService,
                 localization_service: LocalizationService) -> None:
        self.bot = bot
        self.user_service = user_service
        self.t = localization_service.get_string

    @app_commands.command(name="profile", description="Check user profile")
    async def profile_command(self, interaction: discord.Interaction, member: discord.User = None) -> None:
        user = self.user_service.get_and_update_user(interaction.user)
        discord_user = interaction.user
        user_language_id = user.settings.language_id

        if member is not None:
            user = self.user_service.get_user(member)
            discord_user = member

            if user is None:
                await interaction.response.send_message(self.t(user_language_id, 'common.user_not_found'))

        emojis = {emoji.name: str(emoji) for emoji in self.bot.emojis}

        embed = Embed(
            title=f"---------- {self.t(user_language_id, 'profile_cmd.title')} ----------",
            color=YELLOW)
        embed.set_author(name=discord_user.display_name, icon_url=discord_user.display_avatar.url)

        embed.add_field(name=f"{self.t(user_language_id, 'common.pokedollar')}s",
                        value=f"{emojis['pokedollar']} {user.money}")
        embed.add_field(name=f"{self.t(user_language_id, 'common.booster')}s".capitalize(),
                        value=f"{emojis['booster']} {user.boosters_quantity}")
        embed.add_field(name=self.t(user_language_id, 'common.collection').capitalize(),
                        value=f"{emojis['card']} {len(user.cards)}")
        embed.add_field(name=self.t(user_language_id, 'common.last_interaction'),
                        value=discord_tools.timestamp_to_relative_time_format(user.last_interaction_date), inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="cooldowns", description="Check the time you still have to wait for your next commands")
    async def cooldowns_command(self, interaction: discord.Interaction) -> None:
        user = self.user_service.get_and_update_user(interaction.user)
        user_language_id = user.settings.language_id

        embed = Embed(
            title=f"---------- {self.t(user_language_id, 'cooldowns_cmd.title')} ----------",
            color=YELLOW)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)

        available_message = f"{self.t(user_language_id, 'cooldowns_cmd.available')} ✅"

        if time.time() < user.cooldowns.timestamp_for_next_basic_booster:
            basic_booster_cooldown = discord_tools.timestamp_to_relative_time_format(
                user.cooldowns.timestamp_for_next_basic_booster)
        else:
            basic_booster_cooldown = available_message
        embed.add_field(name=f"{self.t(user_language_id, 'common.booster_cooldown')}",
                        value=f"{basic_booster_cooldown}⠀⠀⠀⠀[{self.t(user_language_id, 'cooldowns_cmd.time_between_cmds')} {DEFAULT_BASIC_BOOSTER_COOLDOWN // 60} {self.t(user_language_id, 'common.minutes')}]",
                        inline=False)

        if time.time() < user.cooldowns.timestamp_for_next_promo_booster:
            promo_booster_cooldown = discord_tools.timestamp_to_relative_time_format(
                user.cooldowns.timestamp_for_next_promo_booster)
        else:
            promo_booster_cooldown = available_message
        embed.add_field(name=f"{self.t(user_language_id, 'common.promo_booster_cooldown')}",
                        value=f"{promo_booster_cooldown}⠀⠀⠀⠀[{self.t(user_language_id, 'cooldowns_cmd.time_between_cmds')} {DEFAULT_PROMO_BOOSTER_COOLDOWN // 60} {self.t(user_language_id, 'common.minutes')}]",
                        inline=False)

        await interaction.response.send_message(embed=embed)
