from typing import Optional


class RarityEntity:
    def __init__(self, rarity_name: str, emoji: str, abbreviation: str = "", tier: Optional[int] = None):
        self.name: str = rarity_name
        self.emoji: str = emoji
        self.abbreviation: str = abbreviation
        self.tier = tier
