import json
from pathlib import Path

from starting_data.cities import City

BASE_PATH = Path(__file__).parent

file_city_map: dict[str, City] = {
    "atlanta.json": City.ATLANTA,
    "boston.json": City.BOSTON,
    "calgary.json": City.CALGARY,
    "charleston.json": City.CHARLESTON,
    "chicago.json": City.CHICAGO,
    "dallas.json": City.DALLAS,
    "denver.json": City.DENVER,
    "duluth.json": City.DULUTH,
    "el_paso.json": City.EL_PASO,
    "helena.json": City.HELENA,
    "houston.json": City.HOUSTON,
    "kansas_city.json": City.KANSAS_CITY,
    "las_vegas.json": City.LAS_VEGAS,
    "little_rock.json": City.LITTLE_ROCK,
    "los_angeles.json": City.LOS_ANGELES,
    "miami.json": City.MIAMI,
    "montreal.json": City.MONTREAL,
    "nashville.json": City.NASHVILLE,
    "new_orleans.json": City.NEW_ORLEANS,
    "new_york.json": City.NEW_YORK,
    "oklahoma_city.json": City.OKLAHOMA_CITY,
    "omaha.json": City.OMAHA,
    "phoenix.json": City.PHOENIX,
    "pittsburgh.json": City.PITTSBURGH,
    "portland.json": City.PORTLAND,
    "raleigh.json": City.RALEIGH,
    "salt_lake_city.json": City.SALT_LAKE_CITY,
    "san_francisco.json": City.SAN_FRANCISCO,
    "santa_fe.json": City.SANTA_FE,
    "sault_ste_marie.json": City.SAULT_STE_MARIE,
    "seattle.json": City.SEATTLE,
    "st_louis.json": City.ST_LOUIS,
    "toronto.json": City.TORONTO,
    "vancouver.json": City.VANCOUVER,
    "washington_d_c.json": City.WASHINGTON_D_C,
    "winnipeg.json": City.WINNIPEG,
}


def load_location_json(file_name: str) -> dict:
    file_path = BASE_PATH / "locations" / file_name
    with open(file_path, "r") as f:
        json_location = json.load(f)
    return json_location


def load_all_locations_json() -> list[City, dict]:
    city_json_map: dict[City, dict] = {}

    for file_name in file_city_map.keys():
        json_location = load_location_json(file_name)

        city = file_city_map[file_name]
        city_json_map[city] = json_location

    return city_json_map
