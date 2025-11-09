from route import Route
from starting_data.load_route_json import load_updated_route_json


def build_lines():
    json_routes = load_updated_route_json()
    routes = [Route.from_json(json_route) for json_route in json_routes]

    # verify no duplicate connections
    seen_connections = set()
    for route in routes:
        conn = frozenset({route.a, route.b})
        if conn in seen_connections:
            print(f"Duplicate connection found: {route.a} - {route.b}")
        else:
            seen_connections.add(conn)

    return routes
