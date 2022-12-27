class TypeEntity:
    def __init__(self, type_name: str, emoji: str, abbreviation: str = ""):
        self.name: str = type_name
        self.emoji: str = emoji
        self.abbreviation: str = abbreviation
