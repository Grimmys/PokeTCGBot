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
        self._rarities = [
            RarityEntity("common", "Common", "common"),
            RarityEntity("uncommon", "Uncommon", "uncommon"),
            RarityEntity("rare", "Rare", "rare", tier=0),
            RarityEntity("rare holo", "Rare Holo", "rare_holo", tier=1),
            RarityEntity("rare holo ex", "Rare Holo EX", "rare_holo_ex", tier=2),
            RarityEntity("rare holo gx", "Rare Holo GX", "rare_holo_gx", tier=2),
            RarityEntity("rare holo v", "Rare Holo V", "rare_holo_v", tier=2),
            RarityEntity("rare break", "Rare BREAK", "rare_break", tier=2),
            RarityEntity("double rare", "Double Rare", "double_rare", tier=2),
            RarityEntity("illustration rare", "Illustration Rare", "special", tier=2),
            RarityEntity("radiant rare", "Radiant Rare", "radiant_rare", tier=3),
            RarityEntity("rare holo lv.x", "Rare Holo LV.X", "rare_holo_lvx", tier=3),
            RarityEntity("rare holo vmax", "Rare Holo VMAX", "rare_holo_vmax", tier=3),
            RarityEntity("rare ace", "Rare ACE", "rare_ace", tier=3),
            RarityEntity("rare ultra", "Rare Ultra", "rare_ultra", tier=3),
            RarityEntity("amazing rare", "Amazing Rare", "amazing_rare", tier=3),
            RarityEntity("rare prime", "Rare Prime", "rare_prime", tier=3),
            RarityEntity("rare prism star", "Rare Prism Star", "💫", tier=3),
            RarityEntity("rare shining", "Rare Shining", "rare_shining", tier=3),
            RarityEntity("rare shiny", "Rare Shiny", "rare_shiny", tier=3),
            RarityEntity("ultra rare", "Double Rare Ultra", "double_rare_ultra", tier=3),
            RarityEntity("legend", "LEGEND", "special", tier=4),
            RarityEntity("rare holo star", "Rare Holo Star", "rare_holo_star", tier=4),
            RarityEntity("rare rainbow", "Rare Rainbow", "rare_rainbow", tier=4),
            RarityEntity("rare secret", "Rare Secret", "rare_secret", tier=4),
            RarityEntity("rare shiny gx", "Rare Shiny GX", "rare_shiny_gx", tier=4),
            RarityEntity("rare holo vstar", "Rare Holo VSTAR", "rare_holo_vstar", tier=4),
            RarityEntity("hyper rare", "Hyper Rare", "hyper_rare", tier=4),
            RarityEntity("special illustration rare", "Special Illustration Rare", "special_illustration_rare", tier=4),
            RarityEntity("promo", "Promo", "promo")
        ]
        self._rarities_by_tier = [self._compute_rarities_by_tier(0), self._compute_rarities_by_tier(1),
                                  self._compute_rarities_by_tier(2), self._compute_rarities_by_tier(3),
                                  self._compute_rarities_by_tier(4)]

    def load_rarity_emojis(self, emojis: dict[str, str]):
        for rarity in self._rarities:
            if rarity.emoji[0].isalpha():
                rarity.emoji = emojis[rarity.emoji]

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
