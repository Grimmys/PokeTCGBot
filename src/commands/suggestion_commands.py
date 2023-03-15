import discord
from discord import app_commands
from discord.ext import commands
from discord.app_commands import locale_str as _T

from config import LOG_CHANNEL_ID
from src.services.localization_service import LocalizationService
from src.services.user_service import UserService
from src.utils.flags import is_dev_mode


class SuggestionCog(commands.Cog):
    def __init__(self, bot: commands.Bot, user_service: UserService, localization_service: LocalizationService):
        self.bot = bot
        self._log_channel = None
        self.user_service = user_service
        self._t = localization_service.get_string

    @property
    def log_channel(self):
        if self._log_channel is None:
            self._log_channel = self.bot.get_channel(LOG_CHANNEL_ID)
        return self._log_channel

    @app_commands.command(name=_T("suggestion_cmd-name"), description=_T("suggestion_cmd-desc"))
    async def suggestion_command(self, interaction: discord.Interaction, suggestion: str) -> None:
        user = self.user_service.get_and_update_user(interaction.user, interaction.locale)
        user_language_id = user.settings.language_id

        if not is_dev_mode():
            await interaction.response.send_message(self._t(user_language_id, 'common.feature_disabled'))
            return

        await self.log_channel.send(
            f"{user.id} ({user.name_tag}) made a suggestion: {suggestion}")
        await interaction.response.send_message(self._t(user_language_id, 'suggestion_cmd.response_msg')
                                                .format(emoji="✉️"))
