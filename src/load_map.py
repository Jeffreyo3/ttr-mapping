from src.data_types.cities import City, to_city
from src.data_types.location import Location
from src.starting_data.load_location_json import load_all_locations_json


def build_map() -> dict[City, Location]:
    locations_json_map = load_all_locations_json()

    city_map = {
        city: Location(city, coordinates=locations_json_map[city].get("coordinates"))
        for city in City
    }

    for city, json_data in locations_json_map.items():
        location = city_map[city]
        for conn in json_data.get("connections", []):
            other_city = to_city(conn["city"])
            distance = conn["distance"]
            other_location = city_map[other_city]
            location.add_connection(other_location, distance)

    return city_map
