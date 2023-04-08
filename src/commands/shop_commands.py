from typing import Literal

import discord
from discord import Embed, app_commands
from discord.ext import commands
from discord.app_commands import locale_str as _T

from config import LOG_CHANNEL_ID, BOOSTERS_PRICE, GRADING_PRICE
from src.colors import BLUE
from src.services.localization_service import LocalizationService
from src.services.user_service import UserService


class ShoppingCog(commands.Cog):
    def __init__(self, bot: commands.Bot, user_service: UserService,
                 localization_service: LocalizationService) -> None:
        self.bot = bot
        self._log_channel = None
        self.user_service = user_service
        self._t = localization_service.get_string

    @property
    def log_channel(self):
        if self._log_channel is None:
            self._log_channel = self.bot.get_channel(LOG_CHANNEL_ID)
        return self._log_channel

    @app_commands.command(name=_T("market_booster_cmd-name"), description=_T("market_booster_cmd-desc"))
    async def market_booster_command(self, interaction: discord.Interaction) -> None:
        user = self.user_service.get_and_update_user(interaction.user, interaction.locale)
        user_language_id = user.settings.language_id

        if user.is_banned:
            await interaction.response.send_message(self._t(user_language_id, 'common.user_banned'))
            return

        emojis = {emoji.name: str(emoji) for emoji in self.bot.emojis}

        embed = Embed(
            title=f"---------- {self._t(user_language_id, 'market_booster_cmd.title')} ----------",
            color=BLUE)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)

        embed.add_field(name=f"{emojis['booster']} {self._t(user_language_id, 'common.basic_booster')}",
                        value=f"{emojis['pokedollar']} {BOOSTERS_PRICE['Basic']}")
        embed.add_field(name=f"{emojis['booster_promo']} {self._t(user_language_id, 'common.promo_booster')}",
                        value=f"{emojis['pokedollar']} {BOOSTERS_PRICE['Promo']}")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name=_T("buy_boosters_cmd-name"), description=_T("buy_boosters_cmd-desc"))
    async def buy_boosters_command(self, interaction: discord.Interaction, kind: Literal["basic", "promo"],
                                   quantity: int) -> None:
        user = self.user_service.get_and_update_user(interaction.user, interaction.locale)
        user_language_id = user.settings.language_id

        if user.is_banned:
            await interaction.response.send_message(self._t(user_language_id, 'common.user_banned'))
            return

        if quantity <= 0:
            await interaction.response.send_message(self._t(user_language_id, 'buy_boosters_cmd.negative_quantity'))
            return

        total_price = BOOSTERS_PRICE[kind] * quantity
        if user.money < total_price:
            await interaction.response.send_message(self._t(user_language_id, 'buy_boosters_cmd.not_enough_money'))
            return

        self.user_service.give_money(user.id, - total_price)
        self.user_service.give_boosters(user.id, kind, quantity)
        await self.log_channel.send(f"{user.id} ({user.name_tag}) bought {quantity} {kind} booster(s) for {total_price} Pokémon Dollars")
        await interaction.response.send_message(self._t(user_language_id, 'buy_boosters_cmd.success_buy'))

    @app_commands.command(name=_T("buy_gradings_cmd-name"), description=_T("buy_gradings_cmd-desc"))
    async def buy_gradings_command(self, interaction: discord.Interaction, quantity: int) -> None:
        user = self.user_service.get_and_update_user(interaction.user, interaction.locale)
        user_language_id = user.settings.language_id

        if user.is_banned:
            await interaction.response.send_message(self._t(user_language_id, 'common.user_banned'))
            return

        if quantity <= 0:
            await interaction.response.send_message(self._t(user_language_id, 'buy_gradings_cmd.negative_quantity'))
            return

        total_price = GRADING_PRICE * quantity
        if user.money < total_price:
            await interaction.response.send_message(self._t(user_language_id, 'buy_gradings_cmd.not_enough_money'))
            return

        self.user_service.give_money(user.id, - total_price)
        self.user_service.give_gradings(user.id, quantity)
        await self.log_channel.send(f"{user.id} ({user.name_tag}) bought {quantity} gradings for {total_price} Pokémon Dollars")
        await interaction.response.send_message(self._t(user_language_id, 'buy_gradings_cmd.success_buy'))
