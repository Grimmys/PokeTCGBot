from typing import Literal, List

import discord
from discord import app_commands
from discord.ext import commands
from discord.app_commands import locale_str as _T

from config import BOT_ADMIN_USER_IDS
from src.services.localization_service import LocalizationService
from src.services.set_service import SetService
from src.services.settings_service import SettingsService
from src.services.user_service import UserService


async def booster_kind_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> List[app_commands.Choice[str]]:
    return [
               booster_kind
               for booster_kind in AdminCog.booster_kinds_choices if current.lower() in booster_kind.name.lower()
           ][:25]


class AdminCog(commands.Cog):
    booster_kinds_choices = [
        app_commands.Choice(name="Basic", value="basic"),
        app_commands.Choice(name="Promo", value="promo")
    ]
    booster_kinds = set()

    @staticmethod
    def setup_class(set_service: SetService):
        sets = set_service.get_all_sets_by_id()
        for card_set in sets.values():
            AdminCog.booster_kinds_choices.append(app_commands.Choice(name=card_set.name, value=card_set.id))
        AdminCog.booster_kinds.update({booster_kind_choice.value for booster_kind_choice in
                                       AdminCog.booster_kinds_choices})

    def __init__(self, bot: commands.Bot, settings_service: SettingsService,
                 localization_service: LocalizationService, user_service: UserService) -> None:
        self.bot = bot
        self.settings_service = settings_service
        self.t = localization_service.get_string
        self.user_service = user_service

    @app_commands.command(name="give_money", description="Give or take money to the user")
    async def give_money_command(self, interaction: discord.Interaction, member: discord.User, money: int) -> None:
        user_language_id = self.settings_service.get_user_language_id(interaction.user)

        if interaction.user.id not in BOT_ADMIN_USER_IDS:
            await interaction.response.send_message(self.t(user_language_id, 'common.not_allowed'))
            return

        if self.user_service.give_money(member.id, money):
            await interaction.response.send_message(
                self.t(user_language_id, 'give_money_cmd.response_msg').format(user=f"{member.id} ({member.name})",
                                                                               amount=money))
        else:
            await interaction.response.send_message(
                self.t(user_language_id, 'common.user_not_found'))

    @app_commands.command(name="give_all_money", description="Give or take money to every users")
    async def give_all_money_command(self, interaction: discord.Interaction, money: int) -> None:
        user_language_id = self.settings_service.get_user_language_id(interaction.user)

        if interaction.user.id not in BOT_ADMIN_USER_IDS:
            await interaction.response.send_message(self.t(user_language_id, 'common.not_allowed'))
            return

        if self.user_service.give_all_money(money):
            await interaction.response.send_message(
                self.t(user_language_id, 'give_all_money_cmd.response_msg').format(amount=money))
        else:
            await interaction.response.send_message(
                self.t(user_language_id, 'common.unknown_issue'))

    @app_commands.command(name="give_card", description="Give a card to the user")
    async def give_card_command(self, interaction: discord.Interaction, member: discord.User, card_id: str) -> None:
        user_language_id = self.settings_service.get_user_language_id(interaction.user)

        if interaction.user.id not in BOT_ADMIN_USER_IDS:
            await interaction.response.send_message(self.t(user_language_id, 'common.not_allowed'))
            return

        card_id = card_id.lower()
        if self.user_service.add_cards_to_collection(member.id, [card_id]):
            await interaction.response.send_message(
                self.t(user_language_id, 'give_card_cmd.response_msg').format(user=f"{member.id} ({member.name})",
                                                                              card_id=card_id))
        else:
            await interaction.response.send_message(
                self.t(user_language_id, 'common.user_not_found'))

    @app_commands.command(name="remove_card", description="Remove a card from the user")
    async def remove_card_command(self, interaction: discord.Interaction, member: discord.User, card_id: str) -> None:
        user_language_id = self.settings_service.get_user_language_id(interaction.user)

        if interaction.user.id not in BOT_ADMIN_USER_IDS:
            await interaction.response.send_message(self.t(user_language_id, 'common.not_allowed'))
            return

        card_id = card_id.lower()
        if self.user_service.remove_card_from_collection(member.id, card_id):
            await interaction.response.send_message(
                self.t(user_language_id, 'remove_card_cmd.response_msg').format(user=f"{member.id} ({member.name})",
                                                                                card_id=card_id))
        else:
            await interaction.response.send_message(
                self.t(user_language_id, 'common.user_or_card_not_found'))

    @app_commands.command(name="give_boosters", description="Give some boosters to the user")
    @app_commands.autocomplete(kind=booster_kind_autocomplete)
    async def give_boosters_command(self, interaction: discord.Interaction, member: discord.User,
                                    kind: str, quantity: int) -> None:
        user_language_id = self.settings_service.get_user_language_id(interaction.user)

        if interaction.user.id not in BOT_ADMIN_USER_IDS:
            await interaction.response.send_message(self.t(user_language_id, 'common.not_allowed'))
            return

        if kind not in AdminCog.booster_kinds:
            await interaction.response.send_message(self.t(user_language_id, 'common.invalid_input'))
            return

        if self.user_service.give_boosters(member.id, kind, quantity):
            await interaction.response.send_message(
                self.t(user_language_id, 'give_boosters_cmd.response_msg').format(user=f"{member.id} ({member.name})",
                                                                                  kind=kind, quantity=quantity))
        else:
            await interaction.response.send_message(
                self.t(user_language_id, 'common.user_not_found'))

    @app_commands.command(name="give_all_boosters", description="Give some boosters to every users")
    @app_commands.autocomplete(kind=booster_kind_autocomplete)
    async def give_all_boosters_command(self, interaction: discord.Interaction,
                                        kind: str, quantity: int) -> None:
        user_language_id = self.settings_service.get_user_language_id(interaction.user)

        if interaction.user.id not in BOT_ADMIN_USER_IDS:
            await interaction.response.send_message(self.t(user_language_id, 'common.not_allowed'))
            return

        if kind not in AdminCog.booster_kinds:
            await interaction.response.send_message(self.t(user_language_id, 'common.invalid_input'))
            return

        if self.user_service.give_all_boosters(kind, quantity):
            await interaction.response.send_message(
                self.t(user_language_id, 'give_all_boosters_cmd.response_msg').format(kind=kind, quantity=quantity))
        else:
            await interaction.response.send_message(
                self.t(user_language_id, 'common.unknown_issue'))

    @app_commands.command(name="give_gradings", description="Give some grading actions to the user")
    async def give_gradings_command(self, interaction: discord.Interaction, member: discord.User,
                                    quantity: int) -> None:
        user_language_id = self.settings_service.get_user_language_id(interaction.user)

        if interaction.user.id not in BOT_ADMIN_USER_IDS:
            await interaction.response.send_message(self.t(user_language_id, 'common.not_allowed'))
            return

        if self.user_service.give_gradings(member.id, quantity):
            await interaction.response.send_message(
                self.t(user_language_id, 'give_gradings_cmd.response_msg').format(user=f"{member.id} ({member.name})",
                                                                                  quantity=quantity))
        else:
            await interaction.response.send_message(
                self.t(user_language_id, 'common.user_not_found'))

    @app_commands.command(name=_T("ban_user_cmd-name"), description=_T("ban_user_cmd-desc"))
    async def ban_user_command(self, interaction: discord.Interaction, member: discord.User) -> None:
        user_language_id = self.settings_service.get_user_language_id(interaction.user)

        if interaction.user.id not in BOT_ADMIN_USER_IDS:
            await interaction.response.send_message(self.t(user_language_id, 'common.not_allowed'))
            return

        if self.user_service.ban_user(member.id):
            await interaction.response.send_message(
                self.t(user_language_id, 'ban_user_cmd.response_msg').format(user=f"{member.id} ({member.name})"))
        else:
            await interaction.response.send_message(
                self.t(user_language_id, 'common.user_not_found'))

    @app_commands.command(name=_T("unban_user_cmd-name"), description=_T("unban_user_cmd-desc"))
    async def unban_user_command(self, interaction: discord.Interaction, member: discord.User) -> None:
        user_language_id = self.settings_service.get_user_language_id(interaction.user)

        if interaction.user.id not in BOT_ADMIN_USER_IDS:
            await interaction.response.send_message(self.t(user_language_id, 'common.not_allowed'))
            return

        if self.user_service.unban_user(member.id):
            await interaction.response.send_message(
                self.t(user_language_id, 'unban_user_cmd.response_msg').format(user=f"{member.id} ({member.name})"))
        else:
            await interaction.response.send_message(
                self.t(user_language_id, 'common.user_not_found'))

    @app_commands.command(name="sync", description="Admin command to refresh the commands on each server the bot "
                                                   "currently is")
    async def sync_command(self, interaction: discord.Interaction) -> None:
        user_language_id = self.settings_service.get_user_language_id(interaction.user)

        if interaction.user.id not in BOT_ADMIN_USER_IDS:
            await interaction.response.send_message(self.t(user_language_id, 'common.not_allowed'))
            return

        await interaction.response.defer()
        await self.bot.tree.sync()
        await interaction.edit_original_response(content="All commands have been synced on every servers ✅")
