from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from cities import City, to_city


@dataclass(frozen=True, slots=True)
class Route:
    a: City
    b: City
    value: int

    def __post_init__(self):
        object.__setattr__(self, "a", to_city(self.a))
        object.__setattr__(self, "b", to_city(self.b))

    @classmethod
    def from_triple(cls, triple: tuple[City | str, City | str, int]) -> Route:
        a, b, v = triple
        return cls(a, b, v)

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Route:
        return cls(data["a"], data["b"], data["value"])

    # For checking duplicate connections
    def is_same_connection(self, other: Route) -> bool:
        return (self.a == other.a and self.b == other.b) or (
            self.a == other.b and self.b == other.a
        )
