from typing import Union

from pokemontcgsdk import Card

from src.utils.card_grade import CardGrade

EntryCard = dict[str, Union[Card, int, str, CardGrade]]
