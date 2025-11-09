import json
from pathlib import Path

BASE_PATH = Path(__file__).parent


def load_route_json(file_name: str) -> list[dict]:
    file_path = BASE_PATH / "routes" / file_name
    with open(file_path, "r") as f:
        json_routes = json.load(f)

    return json_routes


def load_original_route_json() -> list[dict]:
    return load_route_json("original.json")


def load_updated_route_json() -> list[dict]:
    return load_route_json("updated_2025.json")
