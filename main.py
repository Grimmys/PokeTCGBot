import asyncio
import logging
from os import environ as env

import discord
from discord import Intents, Embed
from discord.ext.commands import Bot
from pokemontcgsdk import Card, PokemonTcgException

from src.commands.settings_command import SettingsCog
from src.repositories.in_memory_settings_repository import InMemorySettingsRepository
from src.services.localization_service import LocalizationService
from src.services.settings_service import SettingsService

intents = Intents.default()
intents.message_content = True

bot = Bot(intents=intents, command_prefix="")

settings_service = SettingsService(InMemorySettingsRepository())
localization_service = LocalizationService()
t = localization_service.get_string

@bot.tree.command(name="ping", description="Get bot latency")
async def ping_command(interaction: discord.Interaction):
    user_language_id = settings_service.get_user_language_id(interaction.user.id)
    await interaction.response.send_message(
        f"{t(user_language_id, 'ping_cmd.response_msg')} **{round(bot.latency * 1000)}ms**")


@bot.tree.command(name="card", description="Get a card with its id")
async def get_card(interaction: discord.Interaction, card_id: str):
    user_language_id = settings_service.get_user_language_id(interaction.user.id)
    try:
        card = Card.find(card_id)
        embed = Embed(title=card.name, description=card_id, color=0x00ff00)
        embed.set_image(url=card.images.large if card.images.large else card.images.small)
        await interaction.response.send_message(embed=embed)
    except PokemonTcgException:
        await interaction.response.send_message(t(user_language_id, 'get_card_cmd.card_not_found').replace("{1}", card_id))


@bot.event
async def on_ready():
    await bot.tree.sync()


def setup_logs():
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)


async def setup_cogs():
    await bot.add_cog(SettingsCog(bot, settings_service, localization_service))


async def main():
    setup_logs()
    async with bot:
        bot.loop.create_task(setup_cogs())
        await bot.start(env.get("DISCORD_TOKEN"))


if __name__ == "__main__":
    asyncio.run(main())
