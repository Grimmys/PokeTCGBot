from typing import Optional

from src.entities.type_entity import TypeEntity


class TypeService:
    def __init__(self):
        self._types: dict[str, TypeEntity] = {}

    def load_emojis(self, emojis):
        self._types: dict[str, TypeEntity] = {
            "colorless": TypeEntity("colorless", emojis["pokedollar"]),
            "darkness": TypeEntity("darkness", emojis["pokedollar"]),
            "dragon": TypeEntity("dragon", emojis["pokedollar"]),
            "fairy": TypeEntity("fairy", emojis["pokedollar"]),
            "fighting": TypeEntity("fighting", emojis["pokedollar"]),
            "fire": TypeEntity("fire", emojis["pokedollar"]),
            "grass": TypeEntity("grass", emojis["pokedollar"]),
            "lightning": TypeEntity("lightning", emojis["pokedollar"]),
            "metal": TypeEntity("metal", emojis["pokedollar"]),
            "psychic": TypeEntity("psychic", emojis["pokedollar"]),
            "water": TypeEntity("water", emojis["pokedollar"]),
        }

    def get_type(self, type_name: str) -> Optional[TypeEntity]:
        if type_name in self._types:
            return self._types[type_name]
        else:
            print(f"Unrecognized type: {type_name}")
        return None
