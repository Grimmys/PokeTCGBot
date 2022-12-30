class UserCooldownsEntity:
    def __init__(self, timestamp_for_next_basic_booster: int = 0, timestamp_for_next_promo_booster: int = 0):
        self.timestamp_for_next_basic_booster = timestamp_for_next_basic_booster
        self.timestamp_for_next_promo_booster = timestamp_for_next_promo_booster
