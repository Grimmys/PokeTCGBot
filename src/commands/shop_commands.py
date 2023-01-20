from typing import Literal

import discord
from discord import Embed, app_commands
from discord.ext import commands

from src.colors import BLUE
from src.services.localization_service import LocalizationService
from src.services.user_service import UserService

BOOSTERS_PRICE = {
    "Basic": 100,
    "Promo": 300
}


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
                        value=f"{emojis['pokedollar']} {BOOSTERS_PRICE['Basic']}")
        embed.add_field(name=f"{emojis['booster']} {self.t(user_language_id, 'common.promo_booster')}",
                        value=f"{emojis['pokedollar']} {BOOSTERS_PRICE['Promo']}")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="buy_boosters", description="Buy some boosters from market")
    async def buy_boosters_command(self, interaction: discord.Interaction, kind: Literal["Basic", "Promo"],
                                   quantity: int) -> None:
        user = self.user_service.get_and_update_user(interaction.user)
        user_language_id = user.settings.language_id

        if quantity <= 0:
            await interaction.response.send_message(self.t(user_language_id, 'buy_boosters_cmd.negative_quantity'))
            return

        total_price = BOOSTERS_PRICE[kind] * quantity
        if user.money < total_price:
            await interaction.response.send_message(self.t(user_language_id, 'buy_boosters_cmd.not_enough_money'))
            return

        self.user_service.give_money(user.id, - total_price)
        self.user_service.give_boosters(user.id, kind, quantity)
        await interaction.response.send_message(self.t(user_language_id, 'buy_boosters_cmd.success_buy'))
