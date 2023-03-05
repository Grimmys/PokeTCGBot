from typing import Optional

import discord
from discord.app_commands import Translator, locale_str, TranslationContext

from src.services.localization_service import LocalizationService


def timestamp_to_relative_time_format(timestamp: int) -> str:
    return f"<t:{timestamp}:R>"


def format_boolean_option_value(option_value: bool):
    return "✅" if option_value else "❌"


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
