from src.build_all_possible_lines import all_possible_lines
from src.load_map import build_map


map = build_map()
all_distances = all_possible_lines(map)

for cities, distance in all_distances.items():
    city_list = list(cities)
    print(f"{city_list[0].value} - {city_list[1].value} | Distance: {distance}")

print(f"\nTotal unique city pairs: {len(all_distances)}")
