import discord
from discord import app_commands, Embed
from discord.ext import commands
from pokemontcgsdk import Card

SEARCH_PAGE_SIZE=10

class SearchCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot


    @app_commands.command(name="search", description="Search card with several parameters")
    async def search_command(self, interaction: discord.Interaction, content: str) -> None:
        cards = Card.where(q=f"name:*{content}*", page=1, pagesize=SEARCH_PAGE_SIZE)
        embed = Embed()
        for card in cards:
            embed.add_field(name=card.id, value=card.name, inline=False)
        await interaction.response.send_message(embed=embed)
