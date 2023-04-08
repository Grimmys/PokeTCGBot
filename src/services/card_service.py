import os
import pickle
import random

import requests
from PIL import Image, ImageFilter
from pokemontcgsdk import Card

from src.services.localization_service import LocalizationService
from src.utils.card_grade import CardGrade, CARD_GRADE_NAMES

CARDS_PICKLE_FILE_LOCATION = "data/cards.p"


class CardService:
    def __init__(self, localization_service: LocalizationService):
        self._all_cards = pickle.load(open(CARDS_PICKLE_FILE_LOCATION, "rb"))
        self._all_cards_by_id = {card.id.lower(): card for card in self._all_cards}
        self.grade_names_by_language = []
        self.t = localization_service.get_string
        for language in localization_service.supported_languages:
            grade_names = [self.t(language.id, "grade.not_graded").lower(),
                           self.t(language.id, "grade.0").lower(),
                           self.t(language.id, "grade.1").lower(),
                           self.t(language.id, "grade.2").lower(),
                           self.t(language.id, "grade.3").lower()]
            self.grade_names_by_language.append(grade_names)

    def get_card_by_id(self, card_id: str) -> Card:
        return self._all_cards_by_id[card_id]

    def get_all_cards_by_id(self) -> dict[str, Card]:
        return self._all_cards_by_id

    def generate_grade_for_card(self, card: Card, grade: CardGrade) -> None:
        card_name = f"{card.id}_{grade.in_application_name.lower()}.png"
        altered_image_path = f"assets/altered_cards/{card_name}"
        card_not_already_computed = not os.path.isfile(altered_image_path)

        if card_not_already_computed:
            original_image_url = card.images.large if card.images.large else card.images.small
            altered_image = Image.open(requests.get(original_image_url, stream=True).raw)

            if grade.rendering_possible_filters:
                attrition_filter = random.choice(grade.rendering_possible_filters) \
                    .resize(altered_image.size) \
                    .filter(ImageFilter.GaussianBlur(7))
                altered_image.paste(attrition_filter, mask=attrition_filter)

            altered_image.save(altered_image_path)

    def parse_card_id(self, input_card_id: str) -> tuple[str, str]:
        if input_card_id.count("-") == 2:
            actual_card_id, user_grade = input_card_id.rsplit("-", 1)
            user_grade = user_grade.lower()
            for grade_names in self.grade_names_by_language:
                if user_grade in grade_names:
                    actual_grade = CARD_GRADE_NAMES[grade_names.index(user_grade)]
                    break
            else:
                actual_grade = "UNGRADED"
            return actual_card_id.lower(), actual_grade
        return input_card_id.lower(), "UNGRADED"
