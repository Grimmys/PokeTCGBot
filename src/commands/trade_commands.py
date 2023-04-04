import discord
from discord import app_commands, Embed
from discord.app_commands import locale_str as _T
from discord.ext import commands
from discord.ui import View, Button

from config import LOG_CHANNEL_ID
from src.colors import GREEN
from src.services.card_service import CardService
from src.services.localization_service import LocalizationService
from src.services.user_service import UserService
from src.utils.card_grade import card_grade_from
from src.utils.flags import is_dev_mode

TRADE_CARDS_LIMIT = 20


class TradingCog(commands.Cog):
    def __init__(self, bot: commands.Bot, user_service: UserService, card_service: CardService,
                 localization_service: LocalizationService) -> None:
        self.bot = bot
        self._emojis = {}
        self._log_channel = None
        self.user_service = user_service
        self.card_service = card_service
        self._t = localization_service.get_string

    @property
    def emojis(self):
        if not self._emojis:
            self._emojis = {emoji.name: str(emoji) for emoji in self.bot.emojis}
        return self._emojis

    @property
    def log_channel(self):
        if self._log_channel is None:
            self._log_channel = self.bot.get_channel(LOG_CHANNEL_ID)
        return self._log_channel

    @app_commands.command(name=_T("send_cards_cmd-name"), description=_T("send_cards_cmd-desc"))
    async def send_cards_command(self, interaction: discord.Interaction, member: discord.User, card_ids: str) -> None:
        user = self.user_service.get_and_update_user(interaction.user, interaction.locale)
        user_language_id = user.settings.language_id

        if user.is_banned:
            await interaction.response.send_message(self._t(user_language_id, 'common.user_banned'))
            return

        other_user = self.user_service.get_user(member)

        if other_user is None:
            await interaction.response.send_message(self._t(user_language_id, 'common.user_not_found'))
            return

        if user.id == other_user.id:
            await interaction.response.send_message(self._t(user_language_id, 'send_cards_cmd.same_user'))
            return

        parsed_card_ids: list[tuple[str, str]] = [self.card_service.parse_card_id(card_id)
                                                  for card_id in card_ids.split()]
        success_transfer = self.user_service.transfer_cards(user.id, other_user.id, parsed_card_ids)
        if not success_transfer:
            await interaction.response.send_message(self._t(user_language_id, 'send_cards_cmd.missing_cards'))
            return

        await self.log_channel.send(
            f"{user.id} ({user.name_tag}) sent '{card_ids}' card(s) to {other_user.id} ({other_user.name_tag})")
        await interaction.response.send_message(self._t(user_language_id, 'send_cards_cmd.cards_transferred')
                                                .format(user=other_user.name_tag))

    @app_commands.command(name=_T("send_money_cmd-name"), description=_T("send_money_cmd-desc"))
    async def send_money_command(self, interaction: discord.Interaction, member: discord.User, amount: int) -> None:
        user = self.user_service.get_and_update_user(interaction.user, interaction.locale)
        user_language_id = user.settings.language_id

        other_user = self.user_service.get_user(member)

        if other_user is None:
            await interaction.response.send_message(self._t(user_language_id, 'common.user_not_found'))
            return

        if user.id == other_user.id:
            await interaction.response.send_message(self._t(user_language_id, 'send_money_cmd.same_user'))
            return

        if amount <= 0:
            await interaction.response.send_message(self._t(user_language_id, 'send_money_cmd.negative_amount'))
            return

        success_transfer = self.user_service.transfer_money(user.id, other_user.id, amount)
        if not success_transfer:
            await interaction.response.send_message(self._t(user_language_id, 'send_money_cmd.not_enough_money'))
            return

        await self.log_channel.send(
            f"{user.id} ({user.name_tag}) sent {amount} Pokémon Dollars to {other_user.id} ({other_user.name_tag})")
        await interaction.response.send_message(self._t(user_language_id, 'send_money_cmd.money_transferred')
                                                .format(user=other_user.name_tag, amount=amount))

    def _format_card_for_trade(self, card_id: str, grade_name: str, user_language_id: int) -> str:
        card = self.card_service.get_card_by_id(card_id)
        grade_part = ""
        if grade_name != "UNGRADED":
            grade = card_grade_from(grade_name)
            grade_part = f", {self._t(user_language_id, grade.translation_key)}"
        return f"{card_id} ({card.rarity}{grade_part})"

    @app_commands.command(name=_T("secured_trade_cmd-name"), description=_T("secured_trade_cmd-desc"))
    async def secured_trade_command(self, interaction: discord.Interaction, member: discord.User, own_card_ids: str,
                                    other_player_card_ids: str) -> None:
        user = self.user_service.get_and_update_user(interaction.user, interaction.locale)
        user_language_id = user.settings.language_id

        if not is_dev_mode():
            await interaction.response.send_message(self._t(user_language_id, 'common.feature_disabled'))
            return

        if user.is_banned:
            await interaction.response.send_message(self._t(user_language_id, 'common.user_banned'))
            return

        other_user = self.user_service.get_user(member)
        if other_user is None:
            await interaction.response.send_message(self._t(user_language_id, 'common.user_not_found'))
            return

        if user.id == other_user.id:
            await interaction.response.send_message(self._t(user_language_id, 'secured_trade_cmd.same_user'))
            return

        own_card_ids_split: set[tuple[str, str]] = set()
        own_money: int = 0
        for item in own_card_ids.split():
            if item.isdigit():
                own_money = int(item)
            else:
                own_card_ids_split.add(self.card_service.parse_card_id(item))
        if len(own_card_ids_split) > TRADE_CARDS_LIMIT:
            await interaction.response.send_message(
                self._t(user_language_id, 'secured_trade_cmd.author_too_many_cards').format(limit=TRADE_CARDS_LIMIT))
            return
        if own_money < 0:
            await interaction.response.send_message(
                self._t(user_language_id, 'secured_trade_cmd.author_negative_amount'))
            return
        if own_money > user.money:
            await interaction.response.send_message(self._t(user_language_id,
                                                            'secured_trade_cmd.author_not_enough_money'))
            return
        if not self.user_service.user_has_cards(user, own_card_ids_split):
            await interaction.response.send_message(self._t(user_language_id, 'secured_trade_cmd.author_missing_cards'))
            return

        other_player_card_ids_split: set[tuple[str, str]] = set()
        other_player_money: int = 0
        for item in other_player_card_ids.split():
            if item.isdigit():
                other_player_money = int(item)
            else:
                own_card_ids_split.add(self.card_service.parse_card_id(item))
        if len(other_player_card_ids_split) > TRADE_CARDS_LIMIT:
            await interaction.response.send_message(self._t(
                user_language_id, 'secured_trade_cmd.other_player_too_many_cards').format(user=other_user.name_tag,
                                                                                          limit=TRADE_CARDS_LIMIT))
            return
        if other_player_money < 0:
            await interaction.response.send_message(self._t(user_language_id,
                                                            'secured_trade_cmd.other_player_negative_amount')
                                                    .format(user=other_user.name_tag))
            return
        if other_player_money > other_user.money:
            await interaction.response.send_message(self._t(user_language_id,
                                                            'secured_trade_cmd.other_player_not_enough_money')
                                                    .format(user=other_user.name_tag))
            return
        if not self.user_service.user_has_cards(other_user, other_player_card_ids_split):
            await interaction.response.send_message(self._t(user_language_id,
                                                            'secured_trade_cmd.other_player_missing_cards')
                                                    .format(user=other_user.name_tag))

        embed = Embed(
            title=f"---------- {self._t(user_language_id, 'secured_trade_cmd.title')} ----------",
            color=GREEN)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)

        formatted_own_card_ids = [self._format_card_for_trade(card_id, grade, user_language_id)
                                  for (card_id, grade) in own_card_ids_split]
        embed.add_field(name=f"{user.name_tag}:",
                        value=", ".join(formatted_own_card_ids) + f", {own_money} {self.emojis['pokedollar']}",
                        inline=False)
        formatted_other_player_card_ids = [self._format_card_for_trade(card_id, grade, user_language_id)
                                           for (card_id, grade) in other_player_card_ids_split]
        embed.add_field(name=f"{other_user.name_tag}:",
                        value=", ".join(
                            formatted_other_player_card_ids) + f", {other_player_money} {self.emojis['pokedollar']}",
                        inline=False)

        async def validate_trade(confirm_interaction: discord.Interaction):
            if confirm_interaction.user.id != other_user.id:
                await confirm_interaction.response.send_message(
                    self._t(user_language_id, 'secured_trade_cmd.wrong_confirmation_user').format(
                        user=other_user.name_tag),
                    delete_after=2
                )
                return

            success_transfer = self.user_service.transfer_cards_and_money(user.id, other_user.id,
                                                                          list(own_card_ids_split), own_money)
            if not success_transfer:
                await confirm_interaction.response.send_message(
                    self._t(user_language_id, 'secured_trade_cmd.author_missing_cards'))
                await self.log_channel.send(
                    f"{user.id} ({user.name_tag}) cannot send '{own_card_ids_split}' card(s) to "
                    f"{other_user.id} ({other_user.name_tag}) in confirmation step of secured trade")
                return

            success_second_transfer = self.user_service.transfer_cards_and_money(other_user.id, user.id,
                                                                                 list(other_player_card_ids_split),
                                                                                 other_player_money)
            if not success_second_transfer:
                self.user_service.transfer_cards_and_money(other_user.id, user.id, list(own_card_ids_split), own_money)
                await confirm_interaction.response.send_message(self._t(user_language_id,
                                                                        'secured_trade_cmd.other_player_missing_cards'))
                await self.log_channel.send(
                    f"{other_user.id} ({other_user.name_tag}) cannot send '{other_player_card_ids_split}' card(s) to "
                    f"{user.id} ({user.name_tag}) in confirmation step of secured trade, "
                    f"reverting first part of the trade")
                return

            await self.log_channel.send(
                f"{user.id} ({user.name_tag}) sent '{own_card_ids_split}' card(s) to "
                f"{other_user.id} ({other_user.name_tag}) through secured trade")
            await self.log_channel.send(
                f"{other_user.id} ({other_user.name_tag}) sent '{other_player_card_ids_split}' card(s) to "
                f"{user.id} ({user.name_tag}) through secured trade")

            await confirm_interaction.response.send_message(
                self._t(user_language_id, 'secured_trade_cmd.trade_confirmed_response_msg'),
                delete_after=2
            )

        view = View()
        confirm_button = Button(
            label=self._t(user_language_id, 'secured_trade_cmd.confirmation_label'),
            style=discord.ButtonStyle.blurple)
        confirm_button.callback = validate_trade
        view.add_item(confirm_button)

        await interaction.response.send_message(embed=embed, view=view)
