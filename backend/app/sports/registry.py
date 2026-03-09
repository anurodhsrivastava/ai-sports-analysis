"""Sport registry singleton."""

from __future__ import annotations

from .base import SportCoach, SportDefinition


class SportRegistry:
    _definitions: dict[str, SportDefinition] = {}
    _coaches: dict[str, SportCoach] = {}

    @classmethod
    def register(cls, definition: SportDefinition, coach: SportCoach) -> None:
        cls._definitions[definition.sport_id] = definition
        cls._coaches[definition.sport_id] = coach

    @classmethod
    def get_definition(cls, sport_id: str) -> SportDefinition:
        if sport_id not in cls._definitions:
            raise ValueError(f"Unknown sport: {sport_id}")
        return cls._definitions[sport_id]

    @classmethod
    def get_coach(cls, sport_id: str) -> SportCoach:
        if sport_id not in cls._coaches:
            raise ValueError(f"Unknown sport: {sport_id}")
        return cls._coaches[sport_id]

    @classmethod
    def list_sports(cls) -> list[dict]:
        return [
            {
                "sport_id": d.sport_id,
                "display_name": d.display_name,
                "emoji": d.emoji,
                "description": d.description,
            }
            for d in cls._definitions.values()
        ]

    @classmethod
    def has_sport(cls, sport_id: str) -> bool:
        return sport_id in cls._definitions
