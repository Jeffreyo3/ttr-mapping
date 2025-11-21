from pathlib import Path

from src.build_all_possible_lines import all_possible_lines
from src.create_new_lines import build_lines
from src.load_lines import load_lines
from src.load_map import build_map
from src.output_data.save_route_json import save_route_json
from src.route_efficiency import print_route_efficiency_report
from src.image_processing import visualize_route

map = build_map()
all_distances = all_possible_lines(map)
original_lines = load_lines()
new_lines = build_lines(all_distances)
print(f"Original number of lines: {len(original_lines)}")
print(f"New number of lines: {len(new_lines)}")


print_route_efficiency_report(all_distances, new_lines)

save_route_json(new_lines)

# Visualize routes on the map
map_path = str(Path(__file__).parent / "src" / "starting_data" / "maps" / "US_MAP.jpg")
us_bounds = {
    "min_lat": 25.0,
    "max_lat": 52.0,
    "min_lon": -125.0,
    "max_lon": -66.5,
}

zip_file_path = visualize_route(new_lines, map, map_path, bounds=us_bounds)
print(f"Route visualizations saved to: {zip_file_path}")
