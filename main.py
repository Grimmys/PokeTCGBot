import discord
from discord import Intents, Client, app_commands, Embed, SelectOption
import logging

from discord.ui import Select, View
from pokemontcgsdk import Card, PokemonTcgException

from os import environ as env

intents = Intents.default()
intents.message_content = True

client = Client(intents=intents)
tree = app_commands.CommandTree(client)


@tree.command(name="ping", description="Get bot latency")
async def ping_command(interaction: discord.Interaction):
    await interaction.response.send_message(f"My ping is** {round(client.latency * 1000)}ms**")


@tree.command(name="card", description="Get a card with its id")
async def get_card(interaction: discord.Interaction, card_id: str):
    try:
        card = Card.find(card_id)
        embed = Embed(title=card.name, description=card_id, color=0x00ff00)
        embed.set_image(url=card.images.large if card.images.large else card.images.small)
        await interaction.response.send_message(embed=embed)
    except PokemonTcgException:
        await interaction.response.send_message(f'Card {card_id} does not exist.')


language_options = [
    SelectOption(label="Français", emoji="🇫🇷", value="0", description="Changer la langue en français"),
    SelectOption(label="English", emoji="🇬🇧", value="1", description="Switch to English"),
]


@tree.command(name="settings", description="Change user settings")
async def settings(interaction: discord.Interaction):
    embed = Embed(title="---------- Settings ----------", color=0x808080)
    embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
    embed.add_field(name="Language", value=":flag_gb: English",
                    inline=False)

    async def change_language_callback(language_interaction):
        selected_index = int(select.values[0])
        await language_interaction.response.send_message(
            f"Language changed to: {language_options[selected_index].label}", delete_after=2)

    select = Select(
        placeholder="Change language",
        options=language_options
    )
    select.callback = change_language_callback

    view = View()
    view.add_item(select)

    await interaction.response.send_message(embed=embed, view=view)


@client.event
async def on_ready():
    await tree.sync()


if __name__ == "__main__":
    handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
    client.run(env.get("DISCORD_TOKEN"), log_handler=handler, log_level=logging.DEBUG)
