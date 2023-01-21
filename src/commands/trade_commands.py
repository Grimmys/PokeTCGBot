import discord
from discord import app_commands
from discord.ext import commands

from src.services.localization_service import LocalizationService
from src.services.user_service import UserService


class TradingCog(commands.Cog):
    def __init__(self, bot: commands.Bot, user_service: UserService,
                 localization_service: LocalizationService) -> None:
        self.bot = bot
        self.user_service = user_service
        self.t = localization_service.get_string

    @app_commands.command(name="send_cards", description="Send card(s) to another player")
    async def send_cards_command(self, interaction: discord.Interaction, member: discord.User, card_ids: str) -> None:
        user = self.user_service.get_and_update_user(interaction.user)
        user_language_id = user.settings.language_id

        other_user = self.user_service.get_user(member)

        card_ids_list: list[str] = card_ids.split()

        if other_user is None:
            await interaction.response.send_message(self.t(user_language_id, 'common.user_not_found'))
            return

        if user.id == other_user.id:
            await interaction.response.send_message(self.t(user_language_id, 'send_cards_cmd.same_user'))
            return

        success_transfer = self.user_service.transfer_cards(user.id, other_user.id, card_ids_list)
        if not success_transfer:
            await interaction.response.send_message(self.t(user_language_id, 'send_cards_cmd.missing_cards'))
            return

        await interaction.response.send_message(self.t(user_language_id, 'send_cards_cmd.cards_transferred')
                                                .format(user=other_user.name_tag))
