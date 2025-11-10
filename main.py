from src.build_all_possible_lines import all_possible_lines
from src.create_new_lines import build_lines
from src.load_lines import load_lines
from src.load_map import build_map

map = build_map()
all_distances = all_possible_lines(map)
original_lines = load_lines()
new_lines = build_lines(all_distances)
print(f"Original number of lines: {len(original_lines)}")
print(f"New number of lines: {len(new_lines)}")

from src.route_efficiency import print_route_efficiency_report

print_route_efficiency_report(all_distances, new_lines)
