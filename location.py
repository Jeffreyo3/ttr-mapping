from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

from starting_data.cities import City


@dataclass
class Location:
    name: City
    connections: List[Tuple[Location, int]] = field(default_factory=list, repr=False)

    def add_connection(self, other: Location, distance: int):
        if self._should_create_connection(other, new_distance=distance):
            self.connections.append((other, distance))
            other.connections.append((self, distance))

    def _should_create_connection(self, other: Location, new_distance: int) -> bool:
        for connection, distance in self.connections:
            if connection is other:
                self._validate_connection_distance((connection, distance), new_distance)
                return False
        return True

    def _validate_connection_distance(
        self, connection_info: Tuple[Location, int], new_distance: int
    ) -> None:
        connection, other_distance = connection_info

        if new_distance != other_distance:
            raise ValueError(
                f"Conflicting distances for connection between "
                f"{self.name} and {connection.name}: "
                f"{new_distance} vs {other_distance}"
            )

    def __repr__(self):
        neighbor_names = [f"{loc.name.name}({dist})" for loc, dist in self.connections]
        neighbors_str = ", ".join(neighbor_names) if neighbor_names else "None"
        return f"Location({self.name.name}) -> {neighbors_str}"
