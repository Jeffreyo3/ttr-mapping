from build_map import build_map
from shortest_line import shortest_line_include_stops
from starting_data.cities import City


map = build_map()
distance, full_line = shortest_line_include_stops(City.PORTLAND, City.PHOENIX, map)
print("\n")
print(distance, full_line)
print("\n")
