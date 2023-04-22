from typing import Optional, Sequence

from src.entities.rarity_entity import RarityEntity

TIER_DROP_RATES = [
    40,
    30,
    20,
    8,
    2,
]


class RarityService:
    def __init__(self):
        self._rarities: list[RarityEntity] = [
            RarityEntity("common", "Common", "🌿"),
            RarityEntity("uncommon", "Uncommon", "🍀"),
            RarityEntity("rare", "Rare", "🍁", tier=0),
            RarityEntity("rare holo", "Rare Holo", "⭐", tier=1),
            RarityEntity("rare holo ex", "Rare Holo EX", "🌟", tier=2),
            RarityEntity("rare holo gx", "Rare Holo GX", "🌟", tier=2),
            RarityEntity("rare holo v", "Rare Holo V", "🌟", tier=2),
            RarityEntity("rare break", "Rare BREAK", "🧱", tier=2),
            RarityEntity("double rare", "Double Rare", "💥", tier=2),
            RarityEntity("illustration rare", "Illustration Rare", "🖼️", tier=2),
            RarityEntity("radiant rare", "Radiant Rare", "💥", tier=3),
            RarityEntity("rare holo lv.x", "Rare Holo LV.X", "💥", tier=3),
            RarityEntity("rare holo vmax", "Rare Holo VMAX", "🦖", tier=3),
            RarityEntity("rare ace", "Rare ACE", "🔥", tier=3),
            RarityEntity("rare ultra", "Rare Ultra", "💥", tier=3),
            RarityEntity("amazing rare", "Amazing Rare", "🔥", tier=3),
            RarityEntity("rare prime", "Rare Prime", "🔥", tier=3),
            RarityEntity("rare prism star", "Rare Prism Star", "💫", tier=3),
            RarityEntity("rare shining", "Rare Shining", "✨", tier=3),
            RarityEntity("rare shiny", "Rare Shiny", "✨", tier=3),
            RarityEntity("ultra rare", "Ultra Rare", "💥", tier=3),
            RarityEntity("legend", "LEGEND", "📜", tier=4),
            RarityEntity("rare holo star", "Rare Holo Star", "💫", tier=4),
            RarityEntity("rare rainbow", "Rare Rainbow", "💎", tier=4),
            RarityEntity("rare secret", "Rare Secret", "💎", tier=4),
            RarityEntity("rare shiny gx", "Rare Shiny GX", "✨", tier=4),
            RarityEntity("rare holo vstar", "Rare Holo VSTAR", "💫", tier=4),
            RarityEntity("hyper rare", "Hyper Rare", "💥", tier=4),
            RarityEntity("special illustration rare ", "Special Illustration Rare ", "🖌️", tier=4),
            RarityEntity("promo", "Promo", "💯")
        ]
        self._rarities_by_tier = [self._compute_rarities_by_tier(0), self._compute_rarities_by_tier(1),
                                  self._compute_rarities_by_tier(2), self._compute_rarities_by_tier(3),
                                  self._compute_rarities_by_tier(4)]

    def _compute_rarities_by_tier(self, tier: int) -> Sequence[RarityEntity]:
        return list(filter(lambda rarity: rarity.tier == tier, self._rarities))

    def get_rarity(self, rarity_name: str) -> Optional[RarityEntity]:
        for rarity in self._rarities:
            if rarity.name == rarity_name:
                return rarity
        return None

    def get_all_rarity_names(self) -> Sequence[str]:
        return list(map(lambda rarity: rarity.name, self._rarities))

    def get_rarities_by_tier(self, tier: int) -> Sequence[RarityEntity]:
        if tier < len(self._rarities_by_tier):
            return self._rarities_by_tier[tier]
        return []
