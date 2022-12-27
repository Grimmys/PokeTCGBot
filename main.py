import asyncio
import logging
import random
from os import environ as env

import discord
from discord import Intents, Embed
from discord.ext.commands import Bot
from pokemontcgsdk import Card, PokemonTcgException

from src.commands.booster_command import BoosterCog
from src.commands.mini_game_commands import MiniGamesCog
from src.commands.settings_command import SettingsCog
from src.commands.user_info_commands import UserInfoCog
from src.commands.search_command import SearchCog
from src.repositories.pickle_file_user_repository import PickleFileUserRepository
from src.services.localization_service import LocalizationService
from src.services.rarity_service import RarityService
from src.services.settings_service import SettingsService
from src.services.type_service import TypeService
from src.services.user_service import UserService
from src.colors import GREEN, BLUE

intents = Intents.default()
intents.message_content = True

bot = Bot(intents=intents, command_prefix="")


@bot.tree.command(name="ping", description="Get bot latency")
async def ping_command(interaction: discord.Interaction) -> None:
    user_language_id = settings_service.get_user_language_id(interaction.user.id)
    await interaction.response.send_message(
        f"{t(user_language_id, 'ping_cmd.response_msg')} **{round(bot.latency * 1000)}ms**")


@bot.tree.command(name="card", description="Get a card with its id")
async def get_card_command(interaction: discord.Interaction, card_id: str) -> None:
    user_language_id = settings_service.get_user_language_id(interaction.user.id)
    try:
        card = Card.find(card_id)
        embed = Embed(title=card.name, description=card_id, color=GREEN)
        embed.set_image(url=card.images.large if card.images.large else card.images.small)
        await interaction.response.send_message(embed=embed)
    except PokemonTcgException:
        await interaction.response.send_message(
            t(user_language_id, 'get_card_cmd.card_not_found').replace("{1}", card_id))


@bot.tree.command(name="help", description="Display the list of available commands")
async def help_command(interaction: discord.Interaction) -> None:
    user_language_id = settings_service.get_user_language_id(interaction.user.id)
    embed = Embed(title=f"---------- {t(user_language_id, 'help_cmd.title')} ----------",
                  description=t(user_language_id, 'help_cmd.description'), color=BLUE)
    for command in bot.tree.get_commands():
        embed.add_field(name=command.qualified_name, value=command.description, inline=False)
    await interaction.response.send_message(embed=embed)


@bot.event
async def on_ready():
    await bot.tree.sync()


def setup_logs():
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)


async def setup_cogs():
    await bot.add_cog(SettingsCog(bot, settings_service, localization_service))
    await bot.add_cog(BoosterCog(bot, settings_service, localization_service, rarity_service, type_service))
    await bot.add_cog(UserInfoCog(bot, user_service, localization_service))
    await bot.add_cog(SearchCog(bot, settings_service, localization_service))
    await bot.add_cog(MiniGamesCog(bot, settings_service, localization_service))


def read_token_config():
    with open("config.txt", "r") as config:
        return config.read()


async def main():
    setup_logs()
    async with bot:
        bot.loop.create_task(setup_cogs())
        discord_token = env.get("DISCORD_TOKEN") if env.get("DISCORD_TOKEN") is not None else read_token_config()
        print("Bot starting")
        try:
            await bot.start(discord_token)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    random.seed()

    pickle_file_user_repository = PickleFileUserRepository()
    user_service = UserService(pickle_file_user_repository)
    settings_service = SettingsService(pickle_file_user_repository)
    rarity_service = RarityService()
    type_service = TypeService()
    localization_service = LocalizationService()
    t = localization_service.get_string

    asyncio.run(main())
