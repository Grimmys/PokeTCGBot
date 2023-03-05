class UserSettingsEntity:
    def __init__(self, language_id: int = 0, booster_opening_with_image: bool = True, only_use_booster_stock_with_option: bool = True):
        self.language_id = language_id
        self.booster_opening_with_image = booster_opening_with_image
        self.only_use_action_from_stock_with_option = only_use_booster_stock_with_option

    def __setstate__(self, state):
        self.language_id = state.get("language_id", 0)
        self.booster_opening_with_image = state.get("booster_opening_with_image", True)
        self.only_use_action_from_stock_with_option = state.get("only_use_booster_stock_with_option", False)
