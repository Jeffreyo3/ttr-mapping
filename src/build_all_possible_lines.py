from src.shortest_line import shortest_line

# create a dictionary where the key is a frozenset of two cities and the value is the distance

# iterate over all cities and call shortest_line with every other city
#   - to optimize, skip if the frozenset of the two cities is already in the dictionary
#   - use a flag to allow recalculating from the opposite direction and choose the shorter distance
#   - store the shortest distance in the dictionary


def all_possible_lines(city_map, double_count=False):
    distances = {}
    cities = list(city_map.keys())

    for start in cities:
        for end in cities:
            if start == end:
                continue

            if not double_count and frozenset({start, end}) in distances:
                continue

            distance, _ = shortest_line(start, end, city_map)
            distances[frozenset({start, end})] = distance

    return distances
