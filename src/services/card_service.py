import os
import pickle
import random

import requests
from PIL import Image, ImageFilter
from pokemontcgsdk import Card

from src.utils.card_grade import CardGrade

CARDS_PICKLE_FILE_LOCATION = "data/cards.p"


class CardService:
    def __init__(self):
        self._all_cards = pickle.load(open(CARDS_PICKLE_FILE_LOCATION, "rb"))
        self._card_quality_filters = {
            CardGrade.POOR: [Image.open("assets/quality_filters/poor_card_1.png"),
                             Image.open("assets/quality_filters/poor_card_2.png")],
            CardGrade.AVERAGE: [Image.open("assets/quality_filters/average_card_1.png"),
                                Image.open("assets/quality_filters/average_card_2.png")],
            CardGrade.GOOD: [Image.open("assets/quality_filters/good_card_1.png"),
                             Image.open("assets/quality_filters/good_card_2.png")],
            CardGrade.EXCELLENT: None
        }

    def get_all_cards_by_id(self) -> dict[str, Card]:
        return {card.id: card for card in self._all_cards}

    def generate_grade_for_card(self, card: Card, grade: CardGrade) -> None:
        card_name = f"{card.id}_{grade.value.lower()}.png"
        altered_image_path = f"assets/altered_cards/{card_name}"
        card_not_already_computed = not os.path.isfile(altered_image_path)

        if card_not_already_computed:
            original_image_url = card.images.large if card.images.large else card.images.small
            altered_image = Image.open(requests.get(original_image_url, stream=True).raw)

            possible_attrition_filters = self._card_quality_filters[grade]

            if possible_attrition_filters:
                attrition_filter = random.choice(possible_attrition_filters) \
                    .resize(altered_image.size) \
                    .filter(ImageFilter.GaussianBlur(7))
                altered_image.paste(attrition_filter, mask=attrition_filter)

            altered_image.save(altered_image_path)
