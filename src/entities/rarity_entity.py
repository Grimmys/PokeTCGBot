class RarityEntity:
    def __init__(self, rarity_name: str, emoji: str, abbreviation: str = ""):
        self.name: str = rarity_name
        self.emoji: str = emoji
        self.abbreviation: str = abbreviation
