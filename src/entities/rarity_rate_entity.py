class RarityRateEntity:
    def __init__(self, rarity_name: str, rate: float = 1.0):
        self.name: str = rarity_name
        self.rate: float = rate
