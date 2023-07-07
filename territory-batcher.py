# To summarize what we want to do, in one big script:
#     Get the list of territories
#     For each file (for each Quarter)
#     Get the file
#     Process into tiles
#       For each territory
#         Filter into smaller tiles
#         Get statistics
#         Write statistics to database
#         Write smaller tile to file

import geopandas as gp
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from shapely.geometry import Point
from adjustText import adjust_text

import json
from datetime import datetime



def read_territory_quadkeys() -> dict:
    """Read the list of territories from the file territory_quadkeys.json"""
    with open('territory_quadkeys.json') as f:
        territory_quadkeys = json.load(f)
    return territory_quadkeys

def quarter_start(year: int, q: int) -> datetime:
    if not 1 <= q <= 4:
        raise ValueError("Quarter must be within [1, 2, 3, 4]")

    month = [1, 4, 7, 10]
    return datetime(year, month[q - 1], 1)

def get_tile_url(service_type: str, year: int, q: int) -> str:
    dt = quarter_start(year, q)

    base_url = "https://ookla-open-data.s3-us-west-2.amazonaws.com/shapefiles/performance"
    url = f"{base_url}/type%3D{service_type}/year%3D{dt:%Y}/quarter%3D{q}/{dt:%Y-%m-%d}_performance_{service_type}_tiles.zip"
    return url


def main():
    directory = 'geojson-datasets'
    year = 2023
    quarter = 2
    # Get the list of territories
    territory_quadkeys = read_territory_quadkeys()

    # For each file (for each Quarter) (multiquarter not implemented yet)
    # Get the file
    tile_url = get_tile_url("fixed", year, quarter)
    tile_url

    tiles = gp.read_file(tile_url)
    tiles.head()
    

    

    # Process into tiles
    #   For each territory
    #     Filter into smaller tiles
    #     Get statistics
    #     Write statistics to database
    #     Write smaller tile to file

    # Get the file