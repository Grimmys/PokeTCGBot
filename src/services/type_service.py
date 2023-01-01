from typing import Optional

from src.entities.type_entity import TypeEntity


class TypeService:
    def __init__(self):
        self._types: dict[str, TypeEntity] = {}

    def load_emojis(self, emojis):
        self._types: dict[str, TypeEntity] = {
            "colorless": TypeEntity("colorless", emojis["colorless_type"]),
            "darkness": TypeEntity("darkness", emojis["darkness_type"]),
            "dragon": TypeEntity("dragon", emojis["dragon_type"]),
            "fairy": TypeEntity("fairy", emojis["fairy_type"]),
            "fighting": TypeEntity("fighting", emojis["fighting_type"]),
            "fire": TypeEntity("fire", emojis["fire_type"]),
            "grass": TypeEntity("grass", emojis["grass_type"]),
            "lightning": TypeEntity("lightning", emojis["lightning_type"]),
            "metal": TypeEntity("metal", emojis["metal_type"]),
            "psychic": TypeEntity("psychic", emojis["psychic_type"]),
            "water": TypeEntity("water", emojis["water_type"]),
        }

    def get_type(self, type_name: str) -> Optional[TypeEntity]:
        if type_name in self._types:
            return self._types[type_name]
        else:
            print(f"Unrecognized type: {type_name}")
        return None
