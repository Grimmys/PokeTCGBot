import os
import time

import discord
from PIL import Image
from discord import Embed, app_commands, File
from discord.app_commands import locale_str as _T
from discord.ext import commands

from config import DEFAULT_GRADING_COOLDOWN, FAV_GALLERY_PAGES
from src.colors import YELLOW
from src.components.paginated_embed import PaginatedEmbed
from src.entities.quest_entity import QuestEntity, QuestReward
from src.services.card_service import CardService
from src.services.localization_service import LocalizationService
from src.services.quest_service import QuestService
from src.services.user_service import UserService, DEFAULT_BASIC_BOOSTER_COOLDOWN, DEFAULT_PROMO_BOOSTER_COOLDOWN
from src.utils import discord_tools
from src.utils.discord_tools import format_boolean_option_value
from src.utils.flags import is_dev_mode

FAV_LIST_HORIZONTAL_SIZE = 3
FAV_LIST_VERTICAL_SIZE = 3

EMPTY_SLOT_IMAGE = Image.open("assets/card_background.png")


class UserInfoCog(commands.Cog):
    def __init__(self, bot: commands.Bot, user_service: UserService,
                 localization_service: LocalizationService, quest_service: QuestService,
                 card_service: CardService) -> None:
        self.bot = bot
        self.user_service = user_service
        self._t = localization_service.get_string
        self.quest_service = quest_service
        self.card_service = card_service
        self._emojis = {}

    @property
    def emojis(self):
        if not self._emojis:
            self._emojis = {emoji.name: str(emoji) for emoji in self.bot.emojis}
        return self._emojis

    def _compute_quest_reward(self, quest: QuestEntity) -> str:
        match quest.reward_kind:
            case QuestReward.BASIC_BOOSTER:
                return f"{quest.reward_amount} {self.emojis['booster']}"
            case QuestReward.PROMO_BOOSTER:
                return f"{quest.reward_amount} {self.emojis['booster_promo']}"
            case QuestReward.MONEY:
                return f"{quest.reward_amount} {self.emojis['pokedollar']}"
            case _:
                return "Invalid Reward"

    @staticmethod
    def _generate_new_gallery(gallery_path: str) -> None:
        gallery_image = Image.new("RGBA", (FAV_LIST_HORIZONTAL_SIZE * EMPTY_SLOT_IMAGE.size[0],
                                           FAV_LIST_VERTICAL_SIZE * EMPTY_SLOT_IMAGE.size[1]))
        for vertical_position in range(FAV_LIST_VERTICAL_SIZE):
            for horizontal_position in range(FAV_LIST_HORIZONTAL_SIZE):
                gallery_image.paste(EMPTY_SLOT_IMAGE, (horizontal_position * EMPTY_SLOT_IMAGE.size[0],
                                                       vertical_position * EMPTY_SLOT_IMAGE.size[1]))

        gallery_image.save(gallery_path)

    @staticmethod
    def _generate_new_galleries(gallery_base_path: str) -> None:
        for i in range(FAV_GALLERY_PAGES):
            UserInfoCog._generate_new_gallery(f"{gallery_base_path}_{i}.png")

    @app_commands.command(name=_T("profile_cmd-name"), description=_T("profile_cmd-desc"))
    async def profile_command(self, interaction: discord.Interaction, member: discord.User = None) -> None:
        user = self.user_service.get_and_update_user(interaction.user, interaction.locale)
        discord_user = interaction.user
        user_language_id = user.settings.language_id

        if user.is_banned:
            await interaction.response.send_message(self._t(user_language_id, 'common.user_banned'))
            return

        if member is not None:
            user = self.user_service.get_user(member)
            discord_user = member

            if user is None:
                await interaction.response.send_message(self._t(user_language_id, 'common.user_not_found'))

        emojis = {emoji.name: str(emoji) for emoji in self.bot.emojis}

        embed = Embed(
            title=f"---------- {self._t(user_language_id, 'profile_cmd.title')} ----------",
            color=YELLOW)
        embed.set_author(name=discord_user.display_name, icon_url=discord_user.display_avatar.url)

        embed.add_field(name=f"{self._t(user_language_id, 'common.pokedollar')}s",
                        value=f"{emojis['pokedollar']} {user.money}")
        embed.add_field(name=f"{self._t(user_language_id, 'common.basic_booster')}",
                        value=f"{emojis['booster']} {user.boosters_quantity}")
        embed.add_field(name=f"{self._t(user_language_id, 'common.promo_booster')}",
                        value=f"{emojis['booster_promo']} {user.promo_boosters_quantity}")
        embed.add_field(name=f"{self._t(user_language_id, 'common.grading')}s",
                        value=f"🔬 {user.grading_quantity}")
        embed.add_field(name=self._t(user_language_id, 'common.collection').capitalize(),
                        value=f"{emojis['card']} {len(user.cards)}")
        embed.add_field(name=self._t(user_language_id, 'common.last_interaction'),
                        value=discord_tools.timestamp_to_relative_time_format(user.last_interaction_date), inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name=_T("cooldowns_cmd-name"), description=_T("cooldowns_cmd-desc"))
    async def cooldowns_command(self, interaction: discord.Interaction) -> None:
        user = self.user_service.get_and_update_user(interaction.user, interaction.locale)
        user_language_id = user.settings.language_id

        if user.is_banned:
            await interaction.response.send_message(self._t(user_language_id, 'common.user_banned'))
            return

        embed = Embed(
            title=f"---------- {self._t(user_language_id, 'cooldowns_cmd.title')} ----------",
            color=YELLOW)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)

        available_message = f"{self._t(user_language_id, 'cooldowns_cmd.available')} ✅"

        if time.time() < user.cooldowns.timestamp_for_next_basic_booster:
            basic_booster_cooldown = discord_tools.timestamp_to_relative_time_format(
                user.cooldowns.timestamp_for_next_basic_booster)
        else:
            basic_booster_cooldown = available_message
        embed.add_field(name=f"{self._t(user_language_id, 'common.booster_cooldown')}",
                        value=f"{basic_booster_cooldown}⠀⠀⠀⠀[{self._t(user_language_id, 'cooldowns_cmd.time_between_cmds')} {DEFAULT_BASIC_BOOSTER_COOLDOWN // (60 * 60)} {self._t(user_language_id, 'common.hours')}]",
                        inline=False)

        if time.time() < user.cooldowns.timestamp_for_next_promo_booster:
            promo_booster_cooldown = discord_tools.timestamp_to_relative_time_format(
                user.cooldowns.timestamp_for_next_promo_booster)
        else:
            promo_booster_cooldown = available_message
        embed.add_field(name=f"{self._t(user_language_id, 'common.promo_booster_cooldown')}",
                        value=f"{promo_booster_cooldown}⠀⠀⠀⠀[{self._t(user_language_id, 'cooldowns_cmd.time_between_cmds')} {DEFAULT_PROMO_BOOSTER_COOLDOWN // (60 * 60)} {self._t(user_language_id, 'common.hours')}]",
                        inline=False)

        if time.time() < user.cooldowns.timestamp_for_next_daily:
            daily_cooldown = discord_tools.timestamp_to_relative_time_format(
                user.cooldowns.timestamp_for_next_daily)
        else:
            daily_cooldown = available_message
        embed.add_field(name=f"{self._t(user_language_id, 'common.daily_cooldown')}",
                        value=f"{daily_cooldown}⠀⠀⠀⠀[{self._t(user_language_id, 'cooldowns_cmd.midnight_reset')}]",
                        inline=False)

        if time.time() < user.cooldowns.timestamp_for_next_grading:
            grading_cooldown = discord_tools.timestamp_to_relative_time_format(
                user.cooldowns.timestamp_for_next_grading)
        else:
            grading_cooldown = available_message
        embed.add_field(name=f"{self._t(user_language_id, 'common.grading_cooldown')}",
                        value=f"{grading_cooldown}⠀⠀⠀⠀[{self._t(user_language_id, 'cooldowns_cmd.time_between_cmds')} {DEFAULT_GRADING_COOLDOWN // (60 * 60)} {self._t(user_language_id, 'common.hours')}]",
                        inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name=_T("quests_cmd-name"), description=_T("quests_cmd-desc"))
    async def quests_command(self, interaction: discord.Interaction) -> None:
        user = self.user_service.get_and_update_user(interaction.user, interaction.locale)
        user_language_id = user.settings.language_id

        if user.is_banned:
            await interaction.response.send_message(self._t(user_language_id, 'common.user_banned'))
            return

        embed = Embed(
            title=f"---------- {self._t(user_language_id, 'quests_cmd.title')} ----------",
            color=YELLOW)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)

        for quest in user.daily_quests:
            embed.add_field(name=self.quest_service.compute_quest_description(quest, user_language_id),
                            value=f"{self._compute_quest_reward(quest)} [{quest.progress}/{quest.goal_value}] {format_boolean_option_value(quest.accomplished)}",
                            inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name=_T("set_favorite_card_cmd-name"), description=_T("set_favorite_card_cmd-desc"))
    async def set_favorite_card_command(self, interaction: discord.Interaction, card_id: str,
                                        slot_id: int, page_id: int = 1) -> None:
        user = self.user_service.get_and_update_user(interaction.user, interaction.locale)
        user_language_id = user.settings.language_id

        if not is_dev_mode():
            await interaction.response.send_message(self._t(user_language_id, 'common.feature_disabled'))
            return

        if user.is_banned:
            await interaction.response.send_message(self._t(user_language_id, 'common.user_banned'))
            return

        if slot_id not in range(FAV_LIST_VERTICAL_SIZE * FAV_LIST_HORIZONTAL_SIZE):
            await interaction.response.send_message(self._t(user_language_id, 'set_favorite_card_cmd.invalid_slot_id'))
            return

        if page_id not in range(1, FAV_GALLERY_PAGES + 1):
            await interaction.response.send_message(self._t(user_language_id, 'set_favorite_card_cmd.invalid_page_id'))
            return

        card_id, grade_name = self.card_service.parse_card_id(card_id)
        if (card_id, grade_name) not in user.cards:
            await interaction.response.send_message(self._t(user_language_id, 'set_favorite_card_cmd.missing_card'))
            return

        if grade_name == "UNGRADED":
            await interaction.response.send_message(self._t(user_language_id, 'set_favorite_card_cmd.ungraded_card'))
            return

        user_gallery_path = f"assets/user_fav_cards_list/{user.id}"
        page_gallery_path = f"{user_gallery_path}_{page_id - 1}.png"
        if not os.path.isfile(page_gallery_path):
            self._generate_new_galleries(user_gallery_path)

        card_position = (slot_id % FAV_LIST_HORIZONTAL_SIZE, slot_id // FAV_LIST_HORIZONTAL_SIZE)
        graded_card_path = f"assets/altered_cards/{card_id}_{grade_name}.png"
        graded_card_image = Image.open(graded_card_path)
        graded_card_image = graded_card_image.resize(EMPTY_SLOT_IMAGE.size)

        user_gallery_image = Image.open(page_gallery_path)
        user_gallery_image.paste(graded_card_image, (card_position[0] * EMPTY_SLOT_IMAGE.size[0],
                                                     card_position[1] * EMPTY_SLOT_IMAGE.size[1]))
        user_gallery_image.save(page_gallery_path)

        await interaction.response.send_message(self._t(user_language_id, 'set_favorite_card_cmd.response_msg'))

    @app_commands.command(name=_T("favorite_cards_cmd-name"), description=_T("favorite_cards_cmd-desc"))
    async def favorite_cards_command(self, interaction: discord.Interaction) -> None:
        user = self.user_service.get_and_update_user(interaction.user, interaction.locale)
        user_language_id = user.settings.language_id

        if not is_dev_mode():
            await interaction.response.send_message(self._t(user_language_id, 'common.feature_disabled'))
            return

        if user.is_banned:
            await interaction.response.send_message(self._t(user_language_id, 'common.user_banned'))
            return

        await interaction.response.send_message(self._t(user_language_id, 'common.loading'))

        first_page_gallery_name = f"{user.id}_0.png"
        first_page_gallery_path = f"assets/user_fav_cards_list/{first_page_gallery_name}"
        if not os.path.isfile(first_page_gallery_path):
            self._generate_new_galleries(f"assets/user_fav_cards_list/{user.id}")

        gallery_entries = [{"name": "", "value": "", "image": f"{user.id}_{i}.png"}
                           for i in range(FAV_GALLERY_PAGES)]

        paginated_embed = PaginatedEmbed(interaction, gallery_entries, True, user_language_id,
                                         title=f"---------- {self._t(user_language_id, 'favorite_cards_cmd.title')} ----------",
                                         assets_path="user_fav_cards_list")
        await interaction.edit_original_response(content="", embed=paginated_embed.embed, view=paginated_embed.view,
                                                 attachments=paginated_embed.attachments)
