from enum import Enum


class City(Enum):
    ATLANTA = "Atlanta"
    BOSTON = "Boston"
    CALGARY = "Calgary"
    CHARLESTON = "Charleston"
    CHICAGO = "Chicago"
    DALLAS = "Dallas"
    DENVER = "Denver"
    DULUTH = "Duluth"
    EL_PASO = "El Paso"
    HELENA = "Helena"
    HOUSTON = "Houston"
    KANSAS_CITY = "Kansas City"
    LAS_VEGAS = "Las Vegas"
    LITTLE_ROCK = "Little Rock"
    LOS_ANGELES = "Los Angeles"
    MIAMI = "Miami"
    MONTREAL = "Montreal"
    NASHVILLE = "Nashville"
    NEW_ORLEANS = "New Orleans"
    NEW_YORK = "New York"
    OKLAHOMA_CITY = "Oklahoma City"
    OMAHA = "Omaha"
    PHOENIX = "Phoenix"
    PITTSBURGH = "Pittsburgh"
    PORTLAND = "Portland"
    RALEIGH = "Raleigh"
    SALT_LAKE_CITY = "Salt Lake City"
    SAN_FRANCISCO = "San Francisco"
    SANTA_FE = "Santa Fe"
    SAULT_STE_MARIE = "Sault Ste. Marie"
    SEATTLE = "Seattle"
    ST_LOUIS = "St. Louis"
    TORONTO = "Toronto"
    VANCOUVER = "Vancouver"
    WASHINGTON_D_C = "Washington D.C."
    WINNIPEG = "Winnipeg"


def to_city(x: City | str) -> City:
    if isinstance(x, City):
        return x
    try:
        return City(x)
    except ValueError:
        return City[x.upper()]
