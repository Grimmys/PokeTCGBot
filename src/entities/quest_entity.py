from enum import Enum, auto


class QuestType(Enum):
    BOOSTER = auto()
    GRADE = auto()
    DAILY_CLAIM = auto()


class QuestReward(Enum):
    BASIC_BOOSTER = auto()
    PROMO_BOOSTER = auto()
    MONEY = auto()


class QuestEntity:
    def __init__(self, kind: QuestType, goal_value: int, reward_kind: QuestReward, reward_amount: int,
                 progress: int = 0, accomplished: bool = False, quest_id: int = 0):
        self.id = quest_id
        self.kind = kind
        self.goal_value = goal_value
        self.progress = progress
        self.reward_kind = reward_kind
        self.reward_amount = reward_amount
        self.accomplished = accomplished

    def __setstate__(self, state):
        self.id = state.get("id", 0)
        self.kind = state.get("kind")
        self.goal_value = state.get("goal_value")
        self.progress = state.get("progress", 0)
        self.reward_kind = state.get("reward_kind")
        self.reward_amount = state.get("reward_amount")
        self.accomplished = state.get("accomplished", False)

    def increase_progress(self, value: int = 1):
        self.progress += value
        if self.progress >= self.goal_value:
            self.accomplished = True
