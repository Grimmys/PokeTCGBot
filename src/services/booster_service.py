import pickle
import random
from typing import Sequence, Optional

from pokemontcgsdk import Card

import config
from src.entities.rarity_entity import RarityEntity
from src.entities.rarity_rate_entity import RarityRateEntity
from src.services.rarity_service import RarityService, TIER_DROP_RATES
from src.services.set_service import SetService


class BoosterService:
    CARDS_PICKLE_FILE_LOCATION = "data/cards.p"

    def __init__(self, rarity_service: RarityService, set_service: SetService):
        self.rarity_service = rarity_service
        self.boosters_composition = {
            # Scarlet & Violet
            "sv1": [[RarityRateEntity("common")], [RarityRateEntity("common")], [RarityRateEntity("common")],
                    [RarityRateEntity("common")], [RarityRateEntity("uncommon")], [RarityRateEntity("uncommon")],
                    [RarityRateEntity("uncommon")],
                    [RarityRateEntity("ultra rare", 0.05), RarityRateEntity("double rare", 0.15),
                     RarityRateEntity("rare", 0.8)],
                    [RarityRateEntity("hyper rare", 0.01), RarityRateEntity("special illustration rare", 0.03),
                     RarityRateEntity("illustration rare", 0.08), RarityRateEntity("rare", 0.88)]],
            # Crown Zenith
            "swsh12pt5": [[RarityRateEntity("common")], [RarityRateEntity("common")], [RarityRateEntity("common")],
                          [RarityRateEntity("common")], [RarityRateEntity("common")], [RarityRateEntity("uncommon")],
                          [RarityRateEntity("uncommon")], [RarityRateEntity("uncommon")],
                          [RarityRateEntity("rare secret", 0.01), RarityRateEntity("rare ultra", 0.04),
                           RarityRateEntity("rare holo vmax", 0.025), RarityRateEntity("rare holo vstar", 0.035),
                           RarityRateEntity("rare holo v", 0.1), RarityRateEntity("rare holo", 0.15),
                           RarityRateEntity("rare", 0.64)],
                          [RarityRateEntity("trainer gallery rare secret", 0.008, subset_name="swsh12pt5gg"),
                           RarityRateEntity("trainer gallery rare ultra", 0.03, subset_name="swsh12pt5gg"),
                           RarityRateEntity("trainer gallery rare holo v", 0.07, subset_name="swsh12pt5gg"),
                           RarityRateEntity("trainer gallery rare holo", 0.2, subset_name="swsh12pt5gg"),
                           RarityRateEntity("radiant rare", 0.04), RarityRateEntity("rare", 0.652)]],
            # Silver Tempest
            "swsh12": [[RarityRateEntity("common")], [RarityRateEntity("common")], [RarityRateEntity("common")],
                       [RarityRateEntity("common")], [RarityRateEntity("common")], [RarityRateEntity("uncommon")],
                       [RarityRateEntity("uncommon")], [RarityRateEntity("uncommon")],
                       [RarityRateEntity("rare ultra", 0.04), RarityRateEntity("rare secret", 0.01),
                        RarityRateEntity("rare rainbow", 0.01), RarityRateEntity("rare holo vmax", 0.007),
                        RarityRateEntity("rare holo vstar", 0.03), RarityRateEntity("rare holo v", 0.12),
                        RarityRateEntity("rare holo", 0.4), RarityRateEntity("rare", 0.383)],
                       [RarityRateEntity("trainer gallery rare secret", 0.008, subset_name="swsh12tg"),
                        RarityRateEntity("trainer gallery rare ultra", 0.013, subset_name="swsh12tg"),
                        RarityRateEntity("trainer gallery rare holo v", 0.02, subset_name="swsh12tg"),
                        RarityRateEntity("trainer gallery rare holo", 0.08, subset_name="swsh12tg"),
                        RarityRateEntity("radiant rare", 0.05), RarityRateEntity("rare", 0.829)]],
            # Astral Radiance
            "swsh10": [[RarityRateEntity("common")], [RarityRateEntity("common")], [RarityRateEntity("common")],
                       [RarityRateEntity("common")], [RarityRateEntity("common")], [RarityRateEntity("uncommon")],
                       [RarityRateEntity("uncommon")], [RarityRateEntity("uncommon")],
                       [RarityRateEntity("rare ultra", 0.03), RarityRateEntity("rare secret", 0.008),
                        RarityRateEntity("rare rainbow", 0.01), RarityRateEntity("rare holo vmax", 0.005),
                        RarityRateEntity("rare holo vstar", 0.025), RarityRateEntity("rare holo v", 0.125),
                        RarityRateEntity("rare holo", 0.4), RarityRateEntity("rare", 0.397)],
                       [RarityRateEntity("rare secret", 0.007, subset_name="swsh10tg"),
                        RarityRateEntity("rare ultra", 0.01, subset_name="swsh10tg"),
                        RarityRateEntity("rare holo v", 0.02, subset_name="swsh10tg"),
                        RarityRateEntity("rare holo", 0.08, subset_name="swsh10tg"),
                        RarityRateEntity("radiant rare", 0.05), RarityRateEntity("rare", 0.833)]]
        }
        self.set_booster_kinds = {set_id: set_service.get_set_by_id(set_id) for set_id in self.boosters_composition.keys()}
        self.cards_by_rarity: dict[str, list[Card]] = self._compute_all_cards()

    @staticmethod
    def _filter_cards_for_rarities(cards: list[Card], rarities: Sequence[RarityEntity]) -> list[Card]:
        filtered_cards = []
        for card in cards:
            if card.rarity.lower() in rarities:
                filtered_cards.append(card)
        return filtered_cards

    def _compute_all_cards(self) -> dict[str, list[Card]]:
        cards: list[Card] = pickle.load(open(BoosterService.CARDS_PICKLE_FILE_LOCATION, "rb"))
        # TODO: find out why some cards don't have any rarity and define what should be the default rarity for them
        cards_with_rarity = list(filter(lambda card: card.rarity is not None, cards))
        cards_by_rarity = {
            "tier_0": self._filter_cards_for_rarities(cards_with_rarity, self.rarity_service.get_rarities_by_tier(0)),
            "tier_1": self._filter_cards_for_rarities(cards_with_rarity, self.rarity_service.get_rarities_by_tier(1)),
            "tier_2": self._filter_cards_for_rarities(cards_with_rarity, self.rarity_service.get_rarities_by_tier(2)),
            "tier_3": self._filter_cards_for_rarities(cards_with_rarity, self.rarity_service.get_rarities_by_tier(3)),
            "tier_4": self._filter_cards_for_rarities(cards_with_rarity, self.rarity_service.get_rarities_by_tier(4)),
        }
        for rarity in self.rarity_service.get_all_rarities():
            cards_by_rarity[rarity.name] = self._filter_cards_for_rarities(cards_with_rarity, [rarity])
        return cards_by_rarity

    def _draw_rare_card(self, set_id: Optional[str] = None) -> Card:
        rare_pool = []
        while len(rare_pool) == 0:
            card_tier = random.choices(["tier_0", "tier_1", "tier_2", "tier_3", "tier_4"], weights=TIER_DROP_RATES)[0]
            rare_pool = self.cards_by_rarity[card_tier]
            if set_id is not None:
                rare_pool = list(filter(lambda card: card.set.id == set_id, rare_pool))
        return random.choice(rare_pool)

    def _generate_cards_for_set(self, set_id: str, slots: Sequence[Sequence[RarityRateEntity]]):
        drawn_cards = []

        for slot in slots:
            card_rarity = random.choices(slot, weights=list(map(lambda rarity_rate: rarity_rate.rate, slot)))[0]
            pool = self.cards_by_rarity[card_rarity.name]
            subset_id = card_rarity.subset if card_rarity.subset is not None else set_id
            pool = list(filter(lambda card: card.set.id == subset_id, pool))
            card = random.choice(pool)
            drawn_cards.append(card)

        return drawn_cards

    def generate_booster_cards(self, set_id: Optional[str] = None) -> list[Card]:
        drawn_cards = []

        common_pool = self.cards_by_rarity["common"]
        uncommon_pool = self.cards_by_rarity["uncommon"]

        if set_id is not None:
            if set_id in self.boosters_composition:
                # Follow the specific composition of the set
                return self._generate_cards_for_set(set_id, self.boosters_composition[set_id])

            common_pool = list(filter(lambda card: card.set.id == set_id, common_pool))
            uncommon_pool = list(filter(lambda card: card.set.id == set_id, uncommon_pool))

        # Draw the 5 common cards
        for _ in range(5):
            card = random.choice(common_pool)
            drawn_cards.append(card)

        # Draw the 3 uncommon cards
        uncommon_upgrade_triggered = False
        for _ in range(3):
            if not uncommon_upgrade_triggered and random.random() < config.UNCOMMON_UPGRADE_RATE:
                uncommon_upgrade_triggered = True
                card = self._draw_rare_card(set_id)
            else:
                card = random.choice(uncommon_pool)
            drawn_cards.append(card)

        # Draw the rare or higher card
        card = self._draw_rare_card(set_id)
        drawn_cards.append(card)

        return drawn_cards

    def generate_promo_booster_cards(self) -> list[Card]:
        drawn_cards = []

        # Draw the 3 Promo cards
        for _ in range(3):
            card = random.choice(self.cards_by_rarity["promo"])
            drawn_cards.append(card)

        return drawn_cards
