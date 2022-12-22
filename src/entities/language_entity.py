class LanguageEntity:
    def __init__(self, language_id: int, label: str, emoji: str, description: str, abbreviation: str):
        self.id: int = language_id
        self.label: str = label
        self.emoji: str = emoji
        self.description: str = description
        self.abbreviation: str = abbreviation
