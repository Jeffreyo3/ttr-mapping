import json
from pathlib import Path

BASE_PATH = Path(__file__).parent


def save_route_json(file_name: str, routes: list[dict]) -> None:
    file_path = BASE_PATH / "routes" / file_name
    with open(file_path, "w") as f:
        json.dump(routes, f, indent=2)
