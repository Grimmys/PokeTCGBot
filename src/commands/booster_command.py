import pickle
import random
import time

import discord
from discord import Embed, app_commands
from discord.ext import commands
from pokemontcgsdk import Card, Set

import config
from src.services.localization_service import LocalizationService
from src.services.rarity_service import RarityService
from src.services.settings_service import SettingsService
from src.colors import GREEN, RED
from src.services.type_service import TypeService
from src.services.user_service import UserService

TIER_0_RARITIES = {"Rare"}
TIER_1_RARITIES = {"Rare Holo"}
TIER_2_RARITIES = {"Rare Holo EX", "Rare Holo GX", "Rare Holo V", "Rare BREAK"}
TIER_3_RARITIES = {"Radiant Rare", "Rare Holo LV.C", "Rare Holo VMAX", "Rare ACE", "Rare Ultra", "Amazing Rare",
                   "Rare Prime", "Rare Prism Star", "Rare Shining", "Rare Shiny"}
TIER_4_RARITIES = {"LEGEND", "Rare Holo Star", "Rare Rainbow", "Rare Secret", "Rare Shiny GX", "V-UNION",
                   "Rare Holo VSTAR"}
TIER_DROP_RATES = [
    40,
    30,
    20,
    8,
    2,
]


class BoosterCog(commands.Cog):
    CARDS_PICKLE_FILE_LOCATION = "data/cards.p"

    def __init__(self, bot: commands.Bot, settings_service: SettingsService,
                 localization_service: LocalizationService, user_service: UserService, rarity_service: RarityService,
                 type_service: TypeService) -> None:
        self.bot = bot
        self.settings_service = settings_service
        self.t = localization_service.get_string
        self.user_service = user_service
        self.rarity_service = rarity_service
        self.type_service = type_service
        self.sets: list[Set] = Set.all()
        self.cards_by_rarity: dict[str, list[Card]] = BoosterCog._compute_all_cards()

    @staticmethod
    def _filter_cards_for_rarities(cards: list[Card], rarities: set[str]) -> list[Card]:
        filtered_cards = []
        for card in cards:
            if card.rarity in rarities:
                filtered_cards.append(card)
        return filtered_cards

    @staticmethod
    def _compute_all_cards() -> dict[str, list[Card]]:
        cards: list[Card] = pickle.load(open(BoosterCog.CARDS_PICKLE_FILE_LOCATION, "rb"))
        # TODO: find out why some cards don't have any rarity and define what should be the default rarity for them
        cards_with_rarity = list(filter(lambda card: card.rarity is not None, cards))
        return {
            "common": BoosterCog._filter_cards_for_rarities(cards_with_rarity, {"Common"}),
            "uncommon": BoosterCog._filter_cards_for_rarities(cards_with_rarity, {"Uncommon"}),
            "tier_0": BoosterCog._filter_cards_for_rarities(cards_with_rarity, TIER_0_RARITIES),
            "tier_1": BoosterCog._filter_cards_for_rarities(cards_with_rarity, TIER_1_RARITIES),
            "tier_2": BoosterCog._filter_cards_for_rarities(cards_with_rarity, TIER_2_RARITIES),
            "tier_3": BoosterCog._filter_cards_for_rarities(cards_with_rarity, TIER_3_RARITIES),
            "tier_4": BoosterCog._filter_cards_for_rarities(cards_with_rarity, TIER_4_RARITIES),
            "promo": BoosterCog._filter_cards_for_rarities(cards_with_rarity, {"Promo"})
        }

    def _get_card_type_display(self, card: Card) -> str:
        if card.types is None or len(card.types) == 0:
            return ""
        return f"[{self.type_service.get_type(card.types[0].lower()).emoji}]"

    def _display_card_in_embed(self, card: Card, embed: Embed):
        rarity_emoji = "" if (rarity := self.rarity_service.get_rarity(
            card.rarity.lower())) is None else rarity.emoji
        type_emoji = self._get_card_type_display(card)
        embed.add_field(name=card.id,
                        value=f"{card.name} {type_emoji}\n `{card.rarity} {rarity_emoji}`\n ~ {card.set.name} ~")

    def _draw_rare_card(self) -> Card:
        card_tier = random.choices(["tier_0", "tier_1", "tier_2", "tier_3", "tier_4"], weights=TIER_DROP_RATES)[0]
        return random.choice(self.cards_by_rarity[card_tier])

    @staticmethod
    def _formatted_tier_list(rarity_tier: set[str]) -> str:
        return "\n* ".join(rarity_tier)

    def _generate_booster_cards(self, embed) -> list[Card]:
        drawn_cards = []

        # Draw the 5 common cards
        for _ in range(5):
            card = random.choice(self.cards_by_rarity["common"])
            drawn_cards.append(card)
            self._display_card_in_embed(card, embed)

        # Draw the 3 uncommon cards
        uncommon_upgrade_triggered = False
        for _ in range(3):
            if not uncommon_upgrade_triggered and random.random() < config.UNCOMMON_UPGRADE_RATE:
                uncommon_upgrade_triggered = True
                card = self._draw_rare_card()
            else:
                card = random.choice(self.cards_by_rarity["uncommon"])
            drawn_cards.append(card)
            self._display_card_in_embed(card, embed)

        # Draw the rare or higher card
        card = self._draw_rare_card()
        drawn_cards.append(card)
        self._display_card_in_embed(card, embed)

        return drawn_cards

    def _generate_promo_booster_cards(self, embed) -> list[Card]:
        drawn_cards = []

        # Draw the 3 Promo cards
        for _ in range(3):
            card = random.choice(self.cards_by_rarity["promo"])
            drawn_cards.append(card)
            self._display_card_in_embed(card, embed)

        return drawn_cards

    @app_commands.command(name="booster", description="Open a basic booster")
    async def booster_command(self, interaction: discord.Interaction) -> None:
        user = self.user_service.get_user(interaction.user.id)
        user_language_id = user.settings.language_id

        if user.cooldowns.timestamp_for_next_basic_booster > time.time():
            discord_formatted_timestamp = f"<t:{user.cooldowns.timestamp_for_next_basic_booster}:R>"
            await interaction.response.send_message(
                f"{self.t(user_language_id, 'booster_cmd.cooldown')} {discord_formatted_timestamp}")
        else:
            self.user_service.reset_basic_booster_cooldown(user.id)
            embed = Embed(
                title=f"---------- {self.t(user_language_id, 'booster_cmd.title')} ----------",
                color=GREEN)
            embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)

            drawn_cards = self._generate_booster_cards(embed)

            self.user_service.add_cards_to_collection(user.id, list(map(lambda card: card.id, drawn_cards)))

            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="promo_booster", description="Open a Promo booster")
    async def promo_booster_command(self, interaction: discord.Interaction) -> None:
        user = self.user_service.get_user(interaction.user.id)
        user_language_id = user.settings.language_id

        if user.cooldowns.timestamp_for_next_promo_booster > time.time():
            discord_formatted_timestamp = f"<t:{user.cooldowns.timestamp_for_next_promo_booster}:R>"
            await interaction.response.send_message(
                f"{self.t(user_language_id, 'promo_booster_cmd.cooldown')} {discord_formatted_timestamp}")
        else:
            self.user_service.reset_promo_booster_cooldown(user.id)
            embed = Embed(
                title=f"---------- {self.t(user_language_id, 'promo_booster_cmd.title')} ----------",
                color=RED)
            embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)

            drawn_cards = self._generate_promo_booster_cards(embed)

            self.user_service.add_cards_to_collection(user.id, list(map(lambda card: card.id, drawn_cards)))

            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="drop_rates",
                          description="Get the probability for each tier of cards to be in a booster")
    async def drop_rates_command(self, interaction: discord.Interaction) -> None:
        user_language_id = self.settings_service.get_user_language_id(interaction.user.id)

        embed = Embed(
            title=f"---------- {self.t(user_language_id, 'drop_rates_cmd.title')} ----------",
            description=self.t(user_language_id, 'drop_rates_cmd.description'),
            color=GREEN
        )

        embed.add_field(name=f"Tier 0 - {TIER_DROP_RATES[0]}%".ljust(20, ""),
                        value=f"* {BoosterCog._formatted_tier_list(TIER_0_RARITIES)}")
        embed.add_field(name=f"Tier 1 - {TIER_DROP_RATES[1]}%".ljust(20, ""),
                        value=f"* {BoosterCog._formatted_tier_list(TIER_1_RARITIES)}")
        embed.add_field(name=f"Tier 2 - {TIER_DROP_RATES[2]}%".ljust(5, ""),
                        value=f"* {BoosterCog._formatted_tier_list(TIER_2_RARITIES)}")
        embed.add_field(name=f"Tier 3 - {TIER_DROP_RATES[3]}%".ljust(5, ""),
                        value=f"* {BoosterCog._formatted_tier_list(TIER_3_RARITIES)}")
        embed.add_field(name=f"Tier 4 - {TIER_DROP_RATES[4]}%".ljust(5, ""),
                        value=f"* {BoosterCog._formatted_tier_list(TIER_4_RARITIES)}")

        await interaction.response.send_message(embed=embed)
