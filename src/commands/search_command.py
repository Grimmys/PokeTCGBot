import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button
from pokemontcgsdk import Card

from src.components.paginated_embed import PaginatedEmbed
from src.services.localization_service import LocalizationService
from src.services.settings_service import SettingsService

SEARCH_PAGE_SIZE = 10


class SearchCog(commands.Cog):
    def __init__(self, bot: commands.Bot,  settings_service: SettingsService,
                 localization_service: LocalizationService) -> None:
        self.bot = bot
        self.settings_service = settings_service
        self.t = localization_service.get_string

    @app_commands.command(name="search", description="Search card with several parameters")
    async def search_command(self, interaction: discord.Interaction, content: str) -> None:
        user_language_id = self.settings_service.get_user_language_id(
            interaction.user.id)
        all_cards = [{"name": card.id, "value": card.name}
                     for card in Card.where(q=f"name:*{content}*")]

        if len(all_cards) == 0:
            await interaction.response.send_message(self.t(user_language_id, 'search_cmd.not_found').replace("{1}", content))
            return

        embed = PaginatedEmbed(all_cards, SEARCH_PAGE_SIZE)
        view = View()

        async def change_page_callback(click_interaction: discord.Interaction, forward):
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
