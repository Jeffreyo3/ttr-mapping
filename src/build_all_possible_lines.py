from typing import Dict

from src.data_types.cities import City
from src.shortest_line import shortest_line


# double_count: If True, counts both (A, B) and (B, A) as separate entries and will use the lowest distance for each calculation.
# This should be obsolete if Dijkstra's algorithm is implemented correctly, but is left here for validation.
def all_possible_lines(
    city_map, double_count=False
) -> Dict[frozenset[City, City], int]:
    distances = {}
    cities = list(city_map.keys())

    for start in cities:
        for end in cities:
            if start == end:
                continue

            if not double_count and frozenset({start, end}) in distances:
                continue

            distance, _ = shortest_line(start, end, city_map)

            if double_count and frozenset({start, end}) in distances:
                distance = min(distances[frozenset({start, end})], distance)

            distances[frozenset({start, end})] = distance

    print(f"\nTotal unique city pairs: {len(distances)}")
    return distances
