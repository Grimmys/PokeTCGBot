from typing import Optional

from src.entities.type_entity import TypeEntity


class TypeService:
    def __init__(self):
        self._types: dict[str, TypeEntity] = {
            "colorless": TypeEntity("colorless", "⚪"),
            "darkness": TypeEntity("darkness", "🌑"),
            "dragon": TypeEntity("dragon", "🐉"),
            "fairy": TypeEntity("fairy", "🧚"),
            "fighting": TypeEntity("fighting", "✊"),
            "fire": TypeEntity("fire", "🔥"),
            "grass": TypeEntity("grass", "🌱"),
            "lightning": TypeEntity("lightning", "⚡"),
            "metal": TypeEntity("metal", "⚙️"),
            "psychic": TypeEntity("psychic", "🔮"),
            "water": TypeEntity("water", "💧"),
        }

    def get_type(self, type_name: str) -> Optional[TypeEntity]:
        if type_name in self._types:
            return self._types[type_name]
        return None
