from discord import Intents, Client, app_commands, Embed
import logging
from pokemontcgsdk import Card

from os import environ as env

intents = Intents.default()
intents.message_content = True

client = Client(intents=intents)
tree = app_commands.CommandTree(client)


@tree.command(name="ping", description="Get bot latency")
async def ping_command(interaction):
    await interaction.response.send_message(f"My ping is** {round(client.latency * 1000)}ms**")

    
@tree.command(name="card", description="Get a card with its id")
async def card(interaction, id: str):
    try:
        card = Card.find(id)
        embed = Embed(title=card.name, description=id, color=0x00ff00)
        embed.set_image(url=card.images.large if card.images.large else card.images.small)
        await interaction.response.send_message(embed=embed)
    except:
        await interaction.response.send_message(f'Card {id} does not exist.')


@client.event
async def on_ready():
    await tree.sync()


if __name__ == "__main__":
    handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
    client.run(env.get("DISCORD_TOKEN"), log_handler=handler, log_level=logging.DEBUG)
