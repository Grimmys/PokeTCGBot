import discord
from discord import app_commands
from discord.app_commands import locale_str as _T
from discord.ext import commands

from config import LOG_CHANNEL_ID
from src.components.check_suggestions_embed import CheckSuggestionsEmbed
from src.services.localization_service import LocalizationService
from src.services.suggestion_service import SuggestionService, MAX_SUGGESTION_CONTENT_SIZE
from src.services.user_service import UserService
from src.utils.flags import is_dev_mode

DISCORD_RESPONSE_MESSAGE_MAX_SIZE = 2000


class SuggestionCog(commands.Cog):
    def __init__(self, bot: commands.Bot, localization_service: LocalizationService, user_service: UserService,
                 suggestion_service: SuggestionService):
        self.bot = bot
        self._log_channel = None
        self._t = localization_service.get_string
        self.user_service = user_service
        self.suggestion_service = suggestion_service

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

        if self.suggestion_service.add_suggestion(interaction.user, suggestion):
            await self.log_channel.send(
                f"{user.id} ({user.name_tag}) made a suggestion: {suggestion}")
            await interaction.response.send_message(self._t(user_language_id, 'suggestion_cmd.response_msg')
                                                    .format(emoji="✉️"))
        else:
            log_message = f"{user.id} ({user.name_tag}) tried to make a suggestion: '{suggestion}', but it didn't work"
            if len(log_message) > DISCORD_RESPONSE_MESSAGE_MAX_SIZE:
                log_message = f"{user.id} ({user.name_tag}) tried to make a suggestion, but it was too long"
            await self.log_channel.send(log_message)
            await interaction.response.send_message(
                self._t(user_language_id, 'suggestion_cmd.error_msg').format(emoji="❌",
                                                                             max_size=MAX_SUGGESTION_CONTENT_SIZE))

    @app_commands.command(name=_T("check_suggestions_cmd-name"), description=_T("check_suggestions_cmd-desc"))
    async def check_suggestions_command(self, interaction: discord.Interaction) -> None:
        user = self.user_service.get_and_update_user(interaction.user, interaction.locale)
        user_language_id = user.settings.language_id

        if not is_dev_mode():
            await interaction.response.send_message(self._t(user_language_id, 'common.feature_disabled'))
            return

        suggestions = self.suggestion_service.get_all_suggestions()
        suggestions_for_embed = []
        for suggestion in suggestions:
            if len(suggestion.content) <= MAX_SUGGESTION_CONTENT_SIZE:
                suggestions_for_embed.append({
                                              "suggestion": suggestion,
                                              "name": suggestion.author,
                                              "value": suggestion.content
                                             })

        paginated_embed = CheckSuggestionsEmbed(interaction, suggestions_for_embed, user_language_id, interaction.user,
                                                self.suggestion_service.update_vote_to_suggestion,
                                                self.suggestion_service.remove_suggestion,
                                                title=f"---------- {self._t(user_language_id, 'check_suggestions_cmd.title')} ----------")

        await interaction.response.send_message(embed=paginated_embed.embed, view=paginated_embed.view)
