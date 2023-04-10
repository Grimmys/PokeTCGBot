from typing import Optional, Sequence

from src.entities.rarity_entity import RarityEntity

TIER_0_RARITIES = {"Rare"}
TIER_1_RARITIES = {"Rare Holo"}
TIER_2_RARITIES = {"Rare Holo EX", "Rare Holo GX", "Rare Holo V", "Rare BREAK"}
TIER_3_RARITIES = {"Radiant Rare", "Rare Holo LV.X", "Rare Holo VMAX", "Rare ACE", "Rare Ultra", "Amazing Rare",
                   "Rare Prime", "Rare Prism Star", "Rare Shining", "Rare Shiny"}
TIER_4_RARITIES = {"LEGEND", "Rare Holo Star", "Rare Rainbow", "Rare Secret", "Rare Shiny GX",
                   "Rare Holo VSTAR"}
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
            RarityEntity("common", "🌿"),
            RarityEntity("uncommon", "🍀"),
            RarityEntity("rare", "🍁", tier=0),
            RarityEntity("rare holo", "⭐", tier=1),
            RarityEntity("rare holo ex", "🌟", tier=2),
            RarityEntity("rare holo gx", "🌟", tier=2),
            RarityEntity("rare holo v", "🌟", tier=2),
            RarityEntity("rare break", "🧱", tier=2),
            RarityEntity("radiant rare", "💥", tier=3),
            RarityEntity("rare holo lv.x", "💥", tier=3),
            RarityEntity("rare holo vmax", "🦖", tier=3),
            RarityEntity("rare ace", "🔥", tier=3),
            RarityEntity("rare ultra", "💥", tier=3),
            RarityEntity("amazing rare", "🔥", tier=3),
            RarityEntity("rare prime", "🔥", tier=3),
            RarityEntity("rare prism star", "💫", tier=3),
            RarityEntity("rare shining", "✨", tier=3),
            RarityEntity("rare shiny", "✨", tier=3),
            RarityEntity("legend", "📜", tier=4),
            RarityEntity("rare holo star", "💫", tier=4),
            RarityEntity("rare rainbow", "💎", tier=4),
            RarityEntity("rare secret", "💎", tier=4),
            RarityEntity("rare shiny gx", "✨", tier=4),
            RarityEntity("rare holo vstar", "💫", tier=4),
            RarityEntity("promo", "💯")
        ]

    def get_rarity(self, rarity_name: str) -> Optional[RarityEntity]:
        for rarity in self._rarities:
            if rarity.name == rarity_name:
                return rarity
        return None

    def get_all_rarity_names(self) -> Sequence[str]:
        return list(map(lambda rarity: rarity.name, self._rarities))
