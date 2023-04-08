from typing import Optional, Sequence

from src.entities.rarity_entity import RarityEntity


class RarityService:
    def __init__(self):
        self._rarities: dict[str, RarityEntity] = {
            "common": RarityEntity("common", "🌿"),
            "uncommon": RarityEntity("uncommon", "🍀"),
            "rare": RarityEntity("rare", "🎀"),
            "rare holo": RarityEntity("rare holo", "⭐"),
            "rare holo v": RarityEntity("rare holo v", "🌟"),
            "rare holo ex": RarityEntity("rare holo ex", "🌟"),
            "rare holo gx": RarityEntity("rare holo gx", "🌟"),
            "rare shiny": RarityEntity("rare shiny", "✨"),
            "rare ultra": RarityEntity("rare ultra", "💥"),
            "rare holo lv.x": RarityEntity("rare holo lv.x", "💥"),
            "rare holo vmax": RarityEntity("rare holo vmax", "🦖"),
            "rare rainbow": RarityEntity("rare rainbow", "💎"),
            "rare secret": RarityEntity("rare secret", "💎"),
            "legend": RarityEntity("legend", "📜"),
            "promo": RarityEntity("promo", "💯")
        }

    def get_rarity(self, rarity_name: str) -> Optional[RarityEntity]:
        if rarity_name in self._rarities:
            return self._rarities[rarity_name]
        return None

    def get_all_rarity_names(self) -> Sequence[str]:
        return list(self._rarities.keys())
