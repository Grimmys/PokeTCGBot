import discord
from discord import Embed, app_commands
from discord.ext import commands

from src.services.localization_service import LocalizationService
from src.services.user_service import UserService
from src.colors import YELLOW


class UserInfoCog(commands.Cog):
    def __init__(self, bot: commands.Bot, user_service: UserService,
                 localization_service: LocalizationService) -> None:
        self.bot = bot
        self.user_service = user_service
        self.t = localization_service.get_string

    @app_commands.command(name="profile", description="Check your own user profile")
    async def profile_command(self, interaction: discord.Interaction) -> None:
        user = self.user_service.get_user(interaction.user.id)
        user_language_id = user.settings.language_id
        emojis = {emoji.name: str(emoji) for emoji in self.bot.emojis}

        embed = Embed(
            title=f"---------- {self.t(user_language_id, 'profile_cmd.title')} ----------",
            color=YELLOW)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)

        embed.add_field(name=f"{self.t(user_language_id, 'common.pokedollar')}s",
                        value=f"{emojis['pokedollar']} {user.money}")
        embed.add_field(name=f"{self.t(user_language_id, 'common.booster')}s".capitalize(),
                        value=f"{emojis['booster']} {user.boosters_quantity}")
        embed.add_field(name=self.t(user_language_id, 'common.collection').capitalize(), value=f"{emojis['card']} {len(user.cards)}") 

        await interaction.response.send_message(embed=embed)
