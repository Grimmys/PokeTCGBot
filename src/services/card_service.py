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

    def get_all_cards_by_id(self) -> dict[str, Card]:
        return {card.id: card for card in self._all_cards}

    def generate_grade_for_card(self, card: Card, grade: CardGrade) -> None:
        card_name = f"{card.id}_{grade.in_application_name}.png"
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
