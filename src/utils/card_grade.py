from enum import Enum
from typing import Optional, Sequence

from PIL import Image


class CardGrade:
    def __init__(self, in_application_name: str, translation_key: str, probability: Optional[int] = None,
                 rendering_possible_filters: Optional[Sequence[Image]] = None):
        self.in_application_name = in_application_name
        self.translation_key = translation_key
        self.probability = probability
        self.rendering_possible_filters = rendering_possible_filters

    def __eq__(self, other):
        return self.in_application_name == other.in_application_name


class CardGradeEnum(Enum):
    POOR = 0
    AVERAGE = 1
    GOOD = 2
    EXCELLENT = 3


OBTAINABLE_GRADES: tuple[CardGrade, ...] = (
    CardGrade("poor", "grade.0", 20, [Image.open("assets/quality_filters/poor_card_1.png"),
                                      Image.open("assets/quality_filters/poor_card_2.png")]),
    CardGrade("average", "grade.1", 50, [Image.open("assets/quality_filters/average_card_1.png"),
                                         Image.open("assets/quality_filters/average_card_2.png")]),
    CardGrade("good", "grade.2", 20, [Image.open("assets/quality_filters/good_card_1.png"),
                                      Image.open("assets/quality_filters/good_card_2.png")]),
    CardGrade("excellent", "grade.3", 10)
)

GRADES: tuple[CardGrade, ...] = (CardGrade("ungraded", "grade.not_graded"),) + OBTAINABLE_GRADES


def card_grade_from(name: str) -> CardGrade:
    for grade in GRADES:
        if grade.in_application_name == name:
            return grade
    raise Exception("Unrecognized grade")
