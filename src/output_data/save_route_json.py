import json
from datetime import date
from pathlib import Path
from typing import List

from src.data_types.route import Route

BASE_PATH = Path(__file__).parent


def save_route_json(routes: List[Route]) -> None:
    json_routes = [route.to_json() for route in routes]
    json_routes.sort(key=lambda r: (r["a"], r["b"]))

    today = date.today()
    file_path = BASE_PATH / "routes" / f"{today.year}_{today.month}_updated_routes.json"
    with open(file_path, "w") as f:
        json.dump(json_routes, f, indent=2)
