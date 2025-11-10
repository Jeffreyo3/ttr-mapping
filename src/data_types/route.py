from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from src.data_types.cities import City, to_city


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
    def from_json(cls, data: Dict[str, Any]) -> Route:
        return cls(data["a"], data["b"], data["value"])

    def to_json(self) -> Dict[str, Any]:
        return {"a": self.a.value, "b": self.b.value, "value": self.value}
