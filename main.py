import asyncio
import logging
import random
import uuid
from os import environ as env

import discord
from discord import Intents, Embed
from discord.app_commands import locale_str as _T
from discord.ext.commands import Bot
from psycopg2.pool import SimpleConnectionPool

from config import HOSTNAME, DB_NAME, USERNAME, PASSWORD, PORT_ID, CONNECTION_POOL_MIN_CONNECTIONS, \
    CONNECTION_POOL_MAX_CONNECTIONS, DISCORD_TOKEN, DATABASE_MODE_ENABLED
from src.colors import BLUE
from src.commands.admin_commands import AdminCog
from src.commands.booster_command import BoosterCog
from src.commands.daily_command import DailyCog
from src.commands.grade_commands import GradeCog
from src.commands.mini_game_commands import MiniGamesCog
from src.commands.rankings_command import RankingCog
from src.commands.search_commands import SearchCog
from src.commands.settings_command import SettingsCog
from src.commands.shop_commands import ShoppingCog
from src.commands.suggestion_commands import SuggestionCog
from src.commands.trade_commands import TradingCog
from src.commands.user_info_commands import UserInfoCog
from src.components.paginated_embed import PaginatedEmbed
from src.components.search_cards_embed import SearchCardsEmbed
from src.repositories.pickle_file_suggestion_repository import PickleFileSuggestionRepository
from src.repositories.pickle_file_user_repository import PickleFileUserRepository
from src.repositories.postgres_suggestion_repository import PostgresSuggestionRepository
from src.repositories.postgres_user_repository import PostgresUserRepository
from src.scripts.update_database import update_database_schema
from src.services.card_service import CardService
from src.services.localization_service import LocalizationService
from src.services.quest_service import QuestService
from src.services.rarity_service import RarityService
from src.services.set_service import SetService
from src.services.settings_service import SettingsService
from src.services.suggestion_service import SuggestionService
from src.services.type_service import TypeService
from src.services.user_service import UserService
from src.utils.discord_tools import PTCGTranslator

intents = Intents.default()
intents.message_content = True

bot = Bot(intents=intents, command_prefix=str(uuid.uuid1()))


@bot.tree.command(name=_T("ping_cmd-name"), description=_T("ping_cmd-desc"))
async def ping_command(interaction: discord.Interaction) -> None:
    user_language_id = settings_service.get_user_language_id(interaction.user)
    await interaction.response.send_message(
        f"{t(user_language_id, 'ping_cmd.response_msg')} **{round(bot.latency * 1000)}ms**")


@bot.tree.command(name=_T("bot_infos_cmd-name"), description=_T("bot_infos_cmd-desc"))
async def bot_infos_command(interaction: discord.Interaction) -> None:
    user_language_id = settings_service.get_user_language_id(interaction.user)

    emojis = {emoji.name: str(emoji) for emoji in bot.emojis}

    embed = Embed(title=f"---------- {t(user_language_id, 'bot_infos_cmd.title')} ----------", )
    embed.add_field(name=t(user_language_id, 'bot_infos_cmd.count_servers'), value=f"🗃️ {len(bot.guilds)}",
                    inline=False)
    embed.add_field(name=t(user_language_id, 'bot_infos_cmd.total_users'),
                    value=f"👥 {user_service.get_number_users()}", inline=False)
    embed.add_field(name=t(user_language_id, 'bot_infos_cmd.total_money_in_circulation'),
                    value=f"{emojis['pokedollar']} {user_service.get_sum_money_all_users()}", inline=False)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name=_T("help_cmd-name"), description=_T("help_cmd-desc"))
async def help_command(interaction: discord.Interaction) -> None:
    user_language_id = settings_service.get_user_language_id(interaction.user)

    embed = Embed(title=f"---------- {t(user_language_id, 'help_cmd.title')} ----------",
                  description=t(user_language_id, 'help_cmd.description'), color=BLUE)
    for command in bot.tree.get_commands():
        parsed_qualified_name = command.qualified_name.replace("-", ".")
        localized_qualified_name = t(user_language_id, parsed_qualified_name)
        parsed_description = command.description.replace("-", ".")
        localized_description = t(user_language_id, parsed_description)
        if localized_qualified_name and parsed_description:
            embed.add_field(name=localized_qualified_name, value=localized_description, inline=False)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name=_T("tutorial_cmd-name"), description=_T("tutorial_cmd-desc"))
async def tutorial_command(interaction: discord.Interaction) -> None:
    user_language_id = settings_service.get_user_language_id(interaction.user)

    embed = Embed(title=f"---------- {t(user_language_id, 'tutorial_cmd.title')} ----------",
                  description=t(user_language_id, 'tutorial_cmd.description'), color=BLUE)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name=_T("support_cmd-name"), description=_T("support_cmd-desc"))
async def support_command(interaction: discord.Interaction) -> None:
    user_language_id = settings_service.get_user_language_id(interaction.user)
    embed = Embed(title=f"---------- {t(user_language_id, 'support_cmd.title')} ----------",
                  description=t(user_language_id, 'support_cmd.description'), color=BLUE)
    embed.add_field(name=t(user_language_id, 'support_cmd.discord_server_invitation'),
                    value="https://discord.gg/66dPeCnkVy")
    await interaction.response.send_message(embed=embed)


@bot.event
async def on_ready():
    type_service.load_emojis({emoji.name: str(emoji) for emoji in bot.emojis})


def setup_logs():
    logger = logging.getLogger("discord")
    logger.setLevel(logging.DEBUG)
    logging.getLogger("discord.gateway").setLevel(logging.INFO)
    handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)


async def setup_cogs():
    await bot.add_cog(AdminCog(bot, settings_service, localization_service, user_service))
    await bot.add_cog(SuggestionCog(bot, localization_service, user_service, suggestion_service))
    await bot.add_cog(SettingsCog(bot, settings_service, localization_service, user_service))
    await bot.add_cog(DailyCog(bot, localization_service, user_service, quest_service))
    await bot.add_cog(
        BoosterCog(bot, settings_service, localization_service, user_service,
                   rarity_service, type_service, quest_service))
    await bot.add_cog(ShoppingCog(bot, user_service, localization_service))
    await bot.add_cog(TradingCog(bot, user_service, card_service, localization_service))
    await bot.add_cog(UserInfoCog(bot, user_service, localization_service, quest_service, card_service))
    await bot.add_cog(SearchCog(bot, settings_service, localization_service, user_service, card_service))
    await bot.add_cog(RankingCog(bot, settings_service, localization_service, user_service))
    await bot.add_cog(MiniGamesCog(bot, settings_service, localization_service))
    await bot.add_cog(GradeCog(bot, user_service, localization_service, card_service, quest_service))
    await bot.tree.set_translator(PTCGTranslator(localization_service))


async def main():
    setup_logs()
    async with bot:
        bot.loop.create_task(setup_cogs())
        discord_token = env.get("DISCORD_TOKEN") if env.get("DISCORD_TOKEN") is not None else DISCORD_TOKEN
        print("Bot starting")
        try:
            await bot.start(discord_token)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    random.seed()

    if DATABASE_MODE_ENABLED:
        update_database_schema(SimpleConnectionPool(CONNECTION_POOL_MIN_CONNECTIONS, CONNECTION_POOL_MAX_CONNECTIONS,
                                                    host=HOSTNAME, dbname=DB_NAME, user=USERNAME,
                                                    password=PASSWORD, port=PORT_ID))

    user_repository = PickleFileUserRepository()
    suggestion_repository = PickleFileSuggestionRepository()
    localization_service = LocalizationService()
    suggestion_service = SuggestionService(suggestion_repository)
    card_service = CardService(localization_service)
    set_service = SetService()
    user_service = UserService(user_repository, card_service)
    settings_service = SettingsService(user_repository)
    rarity_service = RarityService()
    type_service = TypeService()
    quest_service = QuestService(localization_service)

    t = localization_service.get_string
    PaginatedEmbed.setup_class(t)
    SearchCardsEmbed.setup_class(rarity_service)
    AdminCog.setup_class(set_service)

    asyncio.run(main())
