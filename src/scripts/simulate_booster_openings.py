import time

from src.services.booster_service import BoosterService
from src.services.rarity_service import RarityService

NUMBER_OF_OPENINGS = 1000
SET_ID = "swsh10"

rarity_service = RarityService()
BoosterService.CARDS_PICKLE_FILE_LOCATION = "../../data/cards.p"
booster_service = BoosterService(rarity_service)

cards = []
simulation_start = time.time()
for _ in range(NUMBER_OF_OPENINGS):
    cards.extend(booster_service.generate_booster_cards(SET_ID))
simulation_end = time.time()

number_of_cards_per_rarity = {}
for card in cards:
    if card.rarity in number_of_cards_per_rarity:
        number_of_cards_per_rarity[card.rarity] += 1
    else:
        number_of_cards_per_rarity[card.rarity] = 1

print(f"Number of cards for each rarity: {number_of_cards_per_rarity}")
rarity_proportions = {rarity: value / NUMBER_OF_OPENINGS for (rarity, value) in number_of_cards_per_rarity.items()}
print(f"Proportions of cards for each rarity: {rarity_proportions}")
print(f"Simulation duration: {(simulation_end - simulation_start):.2f} seconds")
