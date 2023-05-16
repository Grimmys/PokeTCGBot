import pickle
import time

from pokemontcgsdk import Set, Card

CARDS_PICKLE_FILE_LOCATION = "../../data/cards.p"
SETS_PICKLE_FILE_LOCATION = "../../data/sets.p"

card_sets: list[Set] = Set.all()
pickle.dump(card_sets, open(SETS_PICKLE_FILE_LOCATION, "wb"))
print("Saved all sets")

all_cards: list[Card] = []
fetching_start = time.time()
for card_set in card_sets:
    all_cards.extend(Card.where(q=f"set.id:{card_set.id}"))
    print(f"Loaded cards for set {card_set.id}")
fetching_end = time.time()

pickle.dump(all_cards, open(CARDS_PICKLE_FILE_LOCATION, "wb"))
print("Saved all cards")
print(f"Fetching duration: {(fetching_end - fetching_start):.2f} seconds")
