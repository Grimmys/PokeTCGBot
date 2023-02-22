import time

import discord
from discord import app_commands
from discord.ext import commands

from src.services.card_service import CardService
from src.services.localization_service import LocalizationService
from src.services.user_service import UserService
from src.utils import discord_tools
from src.utils.card_grade import CardGrade
from src.utils.flags import is_dev_mode


class GradeCog(commands.Cog):
    def __init__(self, bot: commands.Bot, user_service: UserService,
                 localization_service: LocalizationService, card_service: CardService) -> None:
        self.bot = bot
        self._log_channel = None
        self.user_service = user_service
        self.t = localization_service.get_string
        self.card_service = card_service
        self.cards_by_id = self.card_service.get_all_cards_by_id()

    @app_commands.command(name="grade", description="Grade a given card")
    async def grade_command(self, interaction: discord.Interaction, card_id: str) -> None:
        user = self.user_service.get_and_update_user(interaction.user)
        user_language_id = user.settings.language_id

        if not is_dev_mode():
            await interaction.response.send_message(self.t(user_language_id, 'common.feature_disabled'))
            return

        if user.cooldowns.timestamp_for_next_grading > time.time():
            discord_formatted_timestamp = discord_tools.timestamp_to_relative_time_format(
                user.cooldowns.timestamp_for_next_grading)
            await interaction.response.send_message(
                f"{self.t(user_language_id, 'common.grading_cooldown')} {discord_formatted_timestamp}")
            return

        if card_id not in user.cards:
            await interaction.response.send_message(self.t(user_language_id, 'grade_cmd.no_available_copy'))
            return
        await interaction.response.send_message(self.t(user_language_id, 'common.loading'))

        self.user_service.reset_grading_cooldown(user.id)

        card = self.cards_by_id.get(card_id)
        grade = CardGrade.POOR
        self.card_service.generate_grade_for_card(card, grade)

        self.user_service.grade_user_card(user.id, card_id, grade)

        await interaction.edit_original_response(content=self.t(user_language_id, 'grade_cmd.card_has_been_grade')
                                                 .format(card_id=card_id, grade=grade.value))
