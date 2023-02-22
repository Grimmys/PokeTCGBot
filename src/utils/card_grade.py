from enum import Enum


class CardGrade(str, Enum):
    POOR = "Poor",
    AVERAGE = "Average",
    GOOD = "Good",
    EXCELLENT = "Excellent"
