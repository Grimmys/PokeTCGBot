import pickle
from typing import Sequence

from pokemontcgsdk import Set

SETS_PICKLE_FILE_LOCATION = "data/sets.p"


class SetService:
    def __init__(self):
        self._all_sets: Sequence[Set] = pickle.load(open(SETS_PICKLE_FILE_LOCATION, "rb"))
        self._all_sets_by_id = {card_set.id.lower(): card_set for card_set in self._all_sets}

    def get_all_sets_by_id(self) -> dict[str, Set]:
        return self._all_sets_by_id
