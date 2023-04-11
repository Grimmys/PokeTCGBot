from typing import Optional


class RarityEntity:
    def __init__(self, rarity_name: str, display_name: str, emoji: str, abbreviation: str = "", tier: Optional[int] = None):
        self.name: str = rarity_name
        self.display_name: str = display_name
        self.emoji: str = emoji
        self.abbreviation: str = abbreviation
        self.tier = tier

    def __eq__(self, other: any) -> bool:
        if isinstance(other, RarityEntity):
            return other.name == self.name
        if isinstance(other, str):
            return other == self.name
        return False
