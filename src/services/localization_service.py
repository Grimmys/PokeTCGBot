import json

from src.entities.language_entity import LanguageEntity


class LocalizationService:
    supported_languages = [
        LanguageEntity(0, "Français", "🇫🇷", "Changer la langue en français", "fr"),
        LanguageEntity(1, "English", "🇬🇧", "Switch to English", "en")
    ]

    def __init__(self):
        self.localized_strings = {}
        for language in LocalizationService.supported_languages:
            self.localized_strings[language.abbreviation] = LocalizationService.parse_localization_file(language.abbreviation)

    def get_string(self, language_id: int, string_identifier: str) -> str:
        language_abbreviation = LocalizationService.supported_languages[language_id].abbreviation
        identifier_layers = string_identifier.split(".")
        string = self.localized_strings[language_abbreviation]
        for layer in identifier_layers:
            string = string[layer]
        return string

    @staticmethod
    def parse_localization_file(abbreviated_language) -> dict[str, any]:
        file = open(f"localization/localization_{abbreviated_language}.json", encoding="utf-8")
        data = json.load(file)
        file.close()
        return data
