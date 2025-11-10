from build_all_possible_lines import all_possible_lines
from load_map import build_map
from cities import City

map = build_map()
all_distances = all_possible_lines(map)

for cities, distance in all_distances.items():
    city_list = list(cities)
    print(f"{city_list[0].name} - {city_list[1].name}: {distance}")

print(f"\nTotal unique city pairs: {len(all_distances)}")
