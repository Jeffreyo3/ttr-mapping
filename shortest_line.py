import heapq
from itertools import count
from typing import Dict

from location import Location
from starting_data.cities import City


def shortest_line(start: City, end: City, city_map: Dict[City, Location]):
    return _dijkstra(start, end, city_map)


def shortest_line_include_stops(start: City, end: City, city_map: Dict[City, Location]):
    return _dijkstra(start, end, city_map, include_stops=True)


def _dijkstra(
    start: City, end: City, city_map: Dict[City, Location], include_stops=False
):
    counter = count()
    heap = [(0, next(counter), start)]
    dist = {start: 0}
    prev = {start: None}

    while heap:
        current_distance, _, current_city = heapq.heappop(heap)

        if current_city == end:
            break

        if current_distance != dist[current_city]:
            continue

        for neighbor, distance in city_map[current_city].connections:
            distance_through_current = current_distance + distance
            city = neighbor.name

            if city not in dist or distance_through_current < dist[city]:
                dist[city] = distance_through_current
                prev[city] = current_city
                heapq.heappush(heap, (distance_through_current, next(counter), city))

    if include_stops:
        path = _reconstruct_path_with_distances(prev, end, city_map)
        return dist[end], path
    else:
        return dist[end], None


def _reconstruct_path_with_distances(
    prev: Dict[City, City | None],
    end: City,
    city_map: Dict[City, Location],
) -> str:
    back_path = []
    current_city = end

    while current_city is not None:
        back_path.append(current_city)
        current_city = prev[current_city]

    back_path.reverse()
    path_with_distances = []

    for i in range(len(back_path) - 1):
        city = back_path[i]
        next_city = back_path[i + 1]

        for neighbor, distance in city_map[city].connections:
            if neighbor.name == next_city:
                path_with_distances.append(city.value)
                path_with_distances.append(f"{'🚂' * distance} ({distance})")
                break
    path_with_distances.append(back_path[-1].name)
    return " -> ".join(path_with_distances)
