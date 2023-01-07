import asyncio

import discord
from discord import app_commands, Client
from discord.ext import commands
from discord.ui import View, Button

from src.components.paginated_embed import PaginatedEmbed
from src.entities.user_entity import UserEntity
from src.services.localization_service import LocalizationService
from src.services.settings_service import SettingsService
from src.services.user_service import UserService

SEARCH_PAGE_SIZE = 10


class RankingCog(commands.Cog):

    def __init__(self, bot: commands.Bot, settings_service: SettingsService,
                 localization_service: LocalizationService, user_service: UserService) -> None:
        self.bot = bot
        self.settings_service = settings_service
        self.t = localization_service.get_string
        self.user_service = user_service

    async def _fetch_discord_users_by_id(self, discord_users) -> dict[int, discord.User]:
        discord_users = await asyncio.gather(*[self.bot.fetch_user(user.id) for user in discord_users])
        return {user.id: user for user in discord_users}

    @app_commands.command(name="rankings", description="Get the top users having the most cards")
    async def get_rankings_command(self, interaction: discord.Interaction) -> None:
        user_language_id = self.settings_service.get_user_language_id(interaction.user.id)

        users: list[UserEntity] = self.user_service.get_top_users_collection()

        nb_cards_by_user = []
        rank = 0
        discord_users = await self._fetch_discord_users_by_id(users)
        for user in users:
            rank += 1
            nb_cards_by_user.append({"name": f"{rank}: {discord_users[user.id].name}", "value": str(len(user.cards))})

        embed = PaginatedEmbed(nb_cards_by_user, False, SEARCH_PAGE_SIZE,
                               title=f"---------- {self.t(user_language_id, 'ranking_cmd.title')} ----------",
                               inline=True)

        view = View()

        async def change_page_callback(click_interaction: discord.Interaction, forward):
            if click_interaction.user != interaction.user:
                return
            embed.change_page(forward)
            await interaction.edit_original_response(embed=embed.embed)
            await click_interaction.response.defer()

        next_button = Button(emoji="➡️")
        next_button.callback = lambda click_interaction: change_page_callback(
            click_interaction, True)

        previous_button = Button(emoji="⬅️")
        previous_button.callback = lambda click_interaction: change_page_callback(
            click_interaction, False)

        view.add_item(previous_button)
        view.add_item(next_button)

        await interaction.response.send_message(embed=embed.embed, view=view)
