import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button
from pokemontcgsdk import Card

from src.components.paginated_embed import PaginatedEmbed

SEARCH_PAGE_SIZE = 10


class SearchCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="search", description="Search card with several parameters")
    async def search_command(self, interaction: discord.Interaction, content: str) -> None:
        all_cards = [{"name": card.id, "value": card.name}
                     for card in Card.where(q=f"name:*{content}*")]
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
