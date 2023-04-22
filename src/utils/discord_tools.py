from typing import Optional, List, Sequence

import discord
from discord import app_commands
from discord.app_commands import Translator, locale_str, TranslationContext
from pokemontcgsdk import Set

from src.services.localization_service import LocalizationService

MAX_DISCORD_CHOICES = 25
MAX_DISCORD_SELECT_OPTIONS = 25


def timestamp_to_relative_time_format(timestamp: int) -> str:
    return f"<t:{timestamp}:R>"


def format_boolean_option_value(option_value: bool):
    return "✅" if option_value else "❌"


set_booster_kinds_choices = []
set_booster_kinds = set()

all_booster_kinds_choices = [
    app_commands.Choice(name="Basic", value="basic"),
    app_commands.Choice(name="Promo", value="promo")
]
all_booster_kinds = set()


def setup_booster_kinds_choices(sets: dict[str, Set]) -> None:
    for card_set in sets.values():
        set_booster_kinds_choices.append(app_commands.Choice(name=card_set.name, value=card_set.id))
    set_booster_kinds.update({booster_kind_choice.value for booster_kind_choice in
                              set_booster_kinds_choices})
    all_booster_kinds_choices.extend(set_booster_kinds_choices)
    all_booster_kinds.update({booster_kind_choice.value for booster_kind_choice in
                              all_booster_kinds_choices})


def compute_booster_choices_on_input(available_choices: Sequence[app_commands.Choice],
                                     current_input: str) -> list[app_commands.Choice]:
    return [
               booster_kind
               for booster_kind in available_choices if current_input.lower() in booster_kind.name.lower()
           ][:MAX_DISCORD_CHOICES]


async def set_booster_kind_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    return compute_booster_choices_on_input(set_booster_kinds_choices, current)


async def all_booster_kind_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    return compute_booster_choices_on_input(all_booster_kinds_choices, current)


def get_language_id_from_locale(locale: discord.Locale) -> int:
    match locale:
        case discord.Locale.french:
            return 0
        case discord.Locale.british_english:
            return 1
        case discord.Locale.american_english:
            return 1
        case _:
            return 1


class PTCGTranslator(Translator):
    def __init__(self, localization_service: LocalizationService):
        self.localization_service = localization_service

    async def translate(self, string: locale_str, locale: discord.Locale, context: TranslationContext) -> Optional[str]:
        """
        `locale_str` is the string that is requesting to be translated
        `locale` is the target language to translate to
        `context` is the origin of this string, eg TranslationContext.command_name, etc
        This function must return a string (that's been translated), or `None` to signal no available translation available, and will default to the original.
        """
        language_id = get_language_id_from_locale(locale)
        message_str = string.message.replace("-", ".")
        return self.localization_service.get_string(language_id, message_str)
