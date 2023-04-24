from typing import Optional


class RarityRateEntity:
    def __init__(self, rarity_name: str, rate: float = 1.0, subset_name: Optional[str] = None):
        self.name: str = rarity_name
        self.rate: float = rate
        self.subset: Optional[str] = subset_name
