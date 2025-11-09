from location import Location
from starting_data.cities import City, to_city
from starting_data.load_location_json import load_all_locations_json


def build_map():
    city_map = {city: Location(city) for city in City}
    locations_json_map = load_all_locations_json()

    for city, json_data in locations_json_map.items():
        location = city_map[city]
        for conn in json_data:
            other_city = to_city(conn["city"])
            distance = conn["distance"]
            other_location = city_map[other_city]
            location.add_connection(other_location, distance)

    return city_map
