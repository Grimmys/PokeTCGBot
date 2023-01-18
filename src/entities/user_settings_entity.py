class UserSettingsEntity:
    def __init__(self, language_id: int = 0, booster_opening_with_image: bool = True):
        self.language_id = language_id
        self.booster_opening_with_image = booster_opening_with_image

    def __setstate__(self, state):
        self.language_id = state.get("language_id", 0)
        self.booster_opening_with_image = state.get("booster_opening_with_image", True)
