from typing import Dict

from src.data_types.cities import City
from src.data_types.route import Route

AVERAGE_ROUTE_EFFICIENCY = 1.04


def build_lines(lines: Dict[frozenset[City, City], int]):
    new_lines = []
    for connection, distance in lines.items():
        a, b = connection
        value = int(round(distance * AVERAGE_ROUTE_EFFICIENCY))
        new_lines.append(Route(a=a, b=b, value=value))
    return new_lines
