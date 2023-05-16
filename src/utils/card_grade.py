from enum import Enum
from typing import Optional, Sequence

from PIL import Image

ASSETS_FOLDER_LOCATION = "assets"

class CardGrade:
    def __init__(self, in_application_name: str, translation_key: str, emojis: str, probability: Optional[int] = None,
                 rendering_possible_filters: Optional[Sequence[Image]] = None):
        self.in_application_name = in_application_name
        self.translation_key = translation_key
        self.emojis = emojis
        self.probability = probability
        self.rendering_possible_filters = rendering_possible_filters

    def __eq__(self, other):
        return self.in_application_name == other.in_application_name

    def __hash__(self):
        return hash(self.in_application_name)


class CardGradeEnum(Enum):
    POOR = 0
    AVERAGE = 1
    GOOD = 2
    EXCELLENT = 3


CARD_GRADE_NAMES = ["UNGRADED", "POOR", "AVERAGE", "GOOD", "EXCELLENT"]

OBTAINABLE_GRADES: list[CardGrade] = []
GRADES: list[CardGrade] = []


def load_grades(emojis: dict[str, str]):
    OBTAINABLE_GRADES.extend([
        CardGrade(CARD_GRADE_NAMES[1], "grade.0", emojis["grade_star"],
                  20, [Image.open(f"{ASSETS_FOLDER_LOCATION}/quality_filters/poor_card_1.png"),
                       Image.open(f"{ASSETS_FOLDER_LOCATION}/quality_filters/poor_card_2.png")]),
        CardGrade(CARD_GRADE_NAMES[2], "grade.1", emojis["grade_star"] * 2,
                  50, [Image.open(f"{ASSETS_FOLDER_LOCATION}/quality_filters/average_card_1.png"),
                       Image.open(f"{ASSETS_FOLDER_LOCATION}/quality_filters/average_card_2.png")]),
        CardGrade(CARD_GRADE_NAMES[3], "grade.2", emojis["grade_star"] * 3,
                  20, [Image.open(f"{ASSETS_FOLDER_LOCATION}/quality_filters/good_card_1.png"),
                       Image.open(f"{ASSETS_FOLDER_LOCATION}/quality_filters/good_card_2.png")]),
        CardGrade(CARD_GRADE_NAMES[4], "grade.3", emojis["grade_star"] * 4, 10)
    ])

    GRADES.extend(OBTAINABLE_GRADES)
    GRADES.append(CardGrade(CARD_GRADE_NAMES[0], "grade.not_graded", "❌"))


def card_grade_from(name: str) -> CardGrade:
    for grade in GRADES:
        if grade.in_application_name == name:
            return grade
    raise Exception(f"Unrecognized grade '{name}'")
