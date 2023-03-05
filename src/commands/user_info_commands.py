import time

import discord
from discord import Embed, app_commands
from discord.ext import commands
from discord.app_commands import locale_str as _T

from config import DEFAULT_GRADING_COOLDOWN
from src.entities.quest_entity import QuestType, QuestEntity, QuestReward
from src.services.localization_service import LocalizationService
from src.services.quest_service import QuestService
from src.services.user_service import UserService, DEFAULT_BASIC_BOOSTER_COOLDOWN, DEFAULT_PROMO_BOOSTER_COOLDOWN
from src.colors import YELLOW
from src.utils import discord_tools
from src.utils.discord_tools import format_boolean_option_value


class UserInfoCog(commands.Cog):
    def __init__(self, bot: commands.Bot, user_service: UserService,
                 localization_service: LocalizationService, quest_service: QuestService) -> None:
        self.bot = bot
        self.user_service = user_service
        self._t = localization_service.get_string
        self.quest_service = quest_service
        self._emojis = {}

    @property
    def emojis(self):
        if not self._emojis:
            self._emojis = {emoji.name: str(emoji) for emoji in self.bot.emojis}
        return self._emojis

    def _compute_quest_reward(self, quest: QuestEntity) -> str:
        match quest.reward_kind:
            case QuestReward.BASIC_BOOSTER:
                return f"{quest.reward_amount} {self.emojis['booster']}"
            case QuestReward.PROMO_BOOSTER:
                return f"{quest.reward_amount} {self.emojis['booster_promo']}"
            case QuestReward.MONEY:
                return f"{quest.reward_amount} {self.emojis['pokedollar']}"
            case _:
                return "Invalid Reward"

    @app_commands.command(name=_T("profile_cmd-name"), description=_T("profile_cmd-desc"))
    async def profile_command(self, interaction: discord.Interaction, member: discord.User = None) -> None:
        user = self.user_service.get_and_update_user(interaction.user, interaction.locale)
        discord_user = interaction.user
        user_language_id = user.settings.language_id

        if user.is_banned:
            await interaction.response.send_message(self._t(user_language_id, 'common.user_banned'))
            return

        if member is not None:
            user = self.user_service.get_user(member)
            discord_user = member

            if user is None:
                await interaction.response.send_message(self._t(user_language_id, 'common.user_not_found'))

        emojis = {emoji.name: str(emoji) for emoji in self.bot.emojis}

        embed = Embed(
            title=f"---------- {self._t(user_language_id, 'profile_cmd.title')} ----------",
            color=YELLOW)
        embed.set_author(name=discord_user.display_name, icon_url=discord_user.display_avatar.url)

        embed.add_field(name=f"{self._t(user_language_id, 'common.pokedollar')}s",
                        value=f"{emojis['pokedollar']} {user.money}")
        embed.add_field(name=f"{self._t(user_language_id, 'common.basic_booster')}",
                        value=f"{emojis['booster']} {user.boosters_quantity}")
        embed.add_field(name=f"{self._t(user_language_id, 'common.promo_booster')}",
                        value=f"{emojis['booster_promo']} {user.promo_boosters_quantity}")
        embed.add_field(name=f"{self._t(user_language_id, 'common.grading')}s",
                        value=f"🔬 {user.grading_quantity}")
        embed.add_field(name=self._t(user_language_id, 'common.collection').capitalize(),
                        value=f"{emojis['card']} {len(user.cards)}")
        embed.add_field(name=self._t(user_language_id, 'common.last_interaction'),
                        value=discord_tools.timestamp_to_relative_time_format(user.last_interaction_date), inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name=_T("cooldowns_cmd-name"), description=_T("cooldowns_cmd-desc"))
    async def cooldowns_command(self, interaction: discord.Interaction) -> None:
        user = self.user_service.get_and_update_user(interaction.user, interaction.locale)
        user_language_id = user.settings.language_id

        if user.is_banned:
            await interaction.response.send_message(self._t(user_language_id, 'common.user_banned'))
            return

        embed = Embed(
            title=f"---------- {self._t(user_language_id, 'cooldowns_cmd.title')} ----------",
            color=YELLOW)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)

        available_message = f"{self._t(user_language_id, 'cooldowns_cmd.available')} ✅"

        if time.time() < user.cooldowns.timestamp_for_next_basic_booster:
            basic_booster_cooldown = discord_tools.timestamp_to_relative_time_format(
                user.cooldowns.timestamp_for_next_basic_booster)
        else:
            basic_booster_cooldown = available_message
        embed.add_field(name=f"{self._t(user_language_id, 'common.booster_cooldown')}",
                        value=f"{basic_booster_cooldown}⠀⠀⠀⠀[{self._t(user_language_id, 'cooldowns_cmd.time_between_cmds')} {DEFAULT_BASIC_BOOSTER_COOLDOWN // (60 * 60)} {self._t(user_language_id, 'common.hours')}]",
                        inline=False)

        if time.time() < user.cooldowns.timestamp_for_next_promo_booster:
            promo_booster_cooldown = discord_tools.timestamp_to_relative_time_format(
                user.cooldowns.timestamp_for_next_promo_booster)
        else:
            promo_booster_cooldown = available_message
        embed.add_field(name=f"{self._t(user_language_id, 'common.promo_booster_cooldown')}",
                        value=f"{promo_booster_cooldown}⠀⠀⠀⠀[{self._t(user_language_id, 'cooldowns_cmd.time_between_cmds')} {DEFAULT_PROMO_BOOSTER_COOLDOWN // (60 * 60)} {self._t(user_language_id, 'common.hours')}]",
                        inline=False)

        if time.time() < user.cooldowns.timestamp_for_next_daily:
            daily_cooldown = discord_tools.timestamp_to_relative_time_format(
                user.cooldowns.timestamp_for_next_daily)
        else:
            daily_cooldown = available_message
        embed.add_field(name=f"{self._t(user_language_id, 'common.daily_cooldown')}",
                        value=f"{daily_cooldown}⠀⠀⠀⠀[{self._t(user_language_id, 'cooldowns_cmd.midnight_reset')}]",
                        inline=False)

        if time.time() < user.cooldowns.timestamp_for_next_grading:
            grading_cooldown = discord_tools.timestamp_to_relative_time_format(
                user.cooldowns.timestamp_for_next_grading)
        else:
            grading_cooldown = available_message
        embed.add_field(name=f"{self._t(user_language_id, 'common.grading_cooldown')}",
                        value=f"{grading_cooldown}⠀⠀⠀⠀[{self._t(user_language_id, 'cooldowns_cmd.time_between_cmds')} {DEFAULT_GRADING_COOLDOWN // (60 * 60)} {self._t(user_language_id, 'common.hours')}]",
                        inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name=_T("quests_cmd-name"), description=_T("quests_cmd-desc"))
    async def quests_command(self, interaction: discord.Interaction) -> None:
        user = self.user_service.get_and_update_user(interaction.user, interaction.locale)
        user_language_id = user.settings.language_id

        if user.is_banned:
            await interaction.response.send_message(self._t(user_language_id, 'common.user_banned'))
            return

        embed = Embed(
            title=f"---------- {self._t(user_language_id, 'quests_cmd.title')} ----------",
            color=YELLOW)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)

        for quest in user.daily_quests:
            embed.add_field(name=self.quest_service.compute_quest_description(quest, user_language_id),
                            value=f"{self._compute_quest_reward(quest)} [{quest.progress}/{quest.goal_value}] {format_boolean_option_value(quest.accomplished)}",
                            inline=False)

        await interaction.response.send_message(embed=embed)
