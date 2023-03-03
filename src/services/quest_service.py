from src.entities.quest_entity import QuestType, QuestEntity
from src.services.localization_service import LocalizationService


class QuestService:
    def __init__(self, localization_service: LocalizationService):
        self._t = localization_service.get_string

    def compute_quest_description(self, quest: QuestEntity, user_language_id: int) -> str:
        match quest.kind:
            case QuestType.BOOSTER:
                return self._t(user_language_id, 'quests_cmd.booster_description').format(
                    number=quest.goal_value)
            case QuestType.GRADE:
                return self._t(user_language_id, 'quests_cmd.grade_description').format(
                    number=quest.goal_value)
            case QuestType.DAILY_CLAIM:
                return self._t(user_language_id, 'quests_cmd.daily_claim_description')
            case _:
                return "Invalid Quest"
