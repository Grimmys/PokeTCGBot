class UserCooldownsEntity:
    def __init__(self, timestamp_for_next_basic_booster: int = 0, timestamp_for_next_promo_booster: int = 0,
                 timestamp_for_next_daily: int = 0, timestamp_for_next_grading: int = 0):
        self.timestamp_for_next_basic_booster = timestamp_for_next_basic_booster
        self.timestamp_for_next_promo_booster = timestamp_for_next_promo_booster
        self.timestamp_for_next_daily = timestamp_for_next_daily
        self.timestamp_for_next_grading = timestamp_for_next_grading

    def __setstate__(self, state):
        self.timestamp_for_next_basic_booster = state.get("timestamp_for_next_basic_booster", 0)
        self.timestamp_for_next_promo_booster = state.get("timestamp_for_next_promo_booster", 0)
        self.timestamp_for_next_daily = state.get("timestamp_for_next_daily", 0)
        self.timestamp_for_next_grading = state.get("timestamp_for_next_grading", 0)
