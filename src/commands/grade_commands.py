import random
import time

import discord
from discord import app_commands, Embed
from discord.ext import commands

import config
from src.colors import GREEN
from src.entities.quest_entity import QuestType
from src.services.card_service import CardService
from src.services.localization_service import LocalizationService
from src.services.user_service import UserService
from src.utils import discord_tools
from src.utils.card_grade import CardGrade, OBTAINABLE_GRADES

GRADE_DROP_RATES = [
    20,
    50,
    20,
    10
]


class GradeCog(commands.Cog):
    def __init__(self, bot: commands.Bot, user_service: UserService,
                 localization_service: LocalizationService, card_service: CardService) -> None:
        self.bot = bot
        self._log_channel = None
        self.user_service = user_service
        self.t = localization_service.get_string
        self.card_service = card_service
        self.cards_by_id = self.card_service.get_all_cards_by_id()

    @property
    def log_channel(self):
        if self._log_channel is None:
            self._log_channel = self.bot.get_channel(config.LOG_CHANNEL_ID)
        return self._log_channel

    @app_commands.command(name="grade", description="Grade a given card")
    async def grade_command(self, interaction: discord.Interaction, card_id: str) -> None:
        user = self.user_service.get_and_update_user(interaction.user)
        user_language_id = user.settings.language_id

        if user.cooldowns.timestamp_for_next_grading > time.time():
            discord_formatted_timestamp = discord_tools.timestamp_to_relative_time_format(
                user.cooldowns.timestamp_for_next_grading)
            await interaction.response.send_message(
                f"{self.t(user_language_id, 'common.grading_cooldown')} {discord_formatted_timestamp}")
            return

        if (card_id, "ungraded") not in user.cards:
            await interaction.response.send_message(self.t(user_language_id, 'grade_cmd.no_available_copy'))
            return
        await interaction.response.send_message(self.t(user_language_id, 'common.loading'))

        self.user_service.reset_grading_cooldown(user.id)

        card = self.cards_by_id.get(card_id)
        grade: CardGrade = random.choices(OBTAINABLE_GRADES,
                                          weights=[grade.probability for grade in OBTAINABLE_GRADES])[0]
        self.card_service.generate_grade_for_card(card, grade)

        self.user_service.update_progress_on_quests(user.id, QuestType.GRADE)
        card_has_been_added = self.user_service.grade_user_card(user.id, card_id, grade)

        if not card_has_been_added:
            await self.log_channel.send(
                f"Ungraded copy of {card.id} couldn't be removed for {user.id} ({user.name_tag}) while grading card as '{grade.in_application_name}'")

        await self.log_channel.send(
            f"{user.id} ({user.name_tag}) graded card {card.id} as '{grade.in_application_name}'")
        await interaction.edit_original_response(content=self.t(user_language_id, 'grade_cmd.card_has_been_grade')
                                                 .format(card_id=card_id,
                                                         grade=self.t(user_language_id, grade.translation_key)))

    @app_commands.command(name="grade_rates",
                          description="Get the probability for each card grade")
    async def grade_rates_command(self, interaction: discord.Interaction) -> None:
        user = self.user_service.get_and_update_user(interaction.user)
        user_language_id = user.settings.language_id

        embed = Embed(
            title=f"---------- {self.t(user_language_id, 'grade_rates_cmd.title')} ----------",
            description=self.t(user_language_id, 'grade_rates_cmd.description'),
            color=GREEN
        )

        for grade in OBTAINABLE_GRADES:
            embed.add_field(name=self.t(user_language_id, grade.translation_key),
                            value=f"{grade.probability}%", inline=False)

        await interaction.response.send_message(embed=embed)
