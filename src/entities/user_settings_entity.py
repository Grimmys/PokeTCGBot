class UserSettingsEntity:
    def __init__(self, user_id: int, language_id: int = 0):
        self.user_id = user_id
        self.language_id = language_id
