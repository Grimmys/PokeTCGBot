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


class TradingCog(commands.Cog):
    def __init__(self, bot: commands.Bot, user_service: UserService, card_service: CardService,
                 localization_service: LocalizationService) -> None:
        self.bot = bot
        self._log_channel = None
        self.user_service = user_service
        self.card_service = card_service
        self._t = localization_service.get_string

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

        own_card_ids_split: list[tuple[str, str]] = [self.card_service.parse_card_id(card_id) for
                                                     card_id in own_card_ids.split()]
        if not self.user_service.user_has_cards(user, own_card_ids_split):
            await interaction.response.send_message(self._t(user_language_id, 'secured_trade_cmd.author_missing_cards'))
            return

        other_player_card_ids_split: list[tuple[str, str]] = [self.card_service.parse_card_id(card_id) for
                                                              card_id in other_player_card_ids.split()]
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
        embed.add_field(name=f"{user.name_tag}:", value=", ".join(formatted_own_card_ids), inline=False)
        formatted_other_player_card_ids = [self._format_card_for_trade(card_id, grade, user_language_id)
                                           for (card_id, grade) in other_player_card_ids_split]
        embed.add_field(name=f"{other_user.name_tag}:", value=", ".join(formatted_other_player_card_ids), inline=False)

        async def validate_trade(confirm_interaction: discord.Interaction):
            if confirm_interaction.user.id != other_user.id:
                await confirm_interaction.response.send_message(
                    self._t(user_language_id, 'secured_trade_cmd.wrong_confirmation_user').format(
                        user=other_user.name_tag),
                    delete_after=2
                )
                return

            self.user_service.transfer_cards(user.id, other_user.id, own_card_ids_split)
            self.user_service.transfer_cards(other_user.id, user.id, other_player_card_ids_split)

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
