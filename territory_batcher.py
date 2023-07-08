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
import numpy as np

import json
from datetime import datetime

testing = False

# Create a quick numpy encoder so we can serialize our territory stats to a file
# See: https://stackoverflow.com/a/57915246
class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

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
    # print batch timestamp
    print("Batch started at", datetime.now())
    directory = 'geojson-datasets'
    year = 2023
    quarter = 2
    quarter_year = f'{year}Q{quarter}'
    # Initialize the stats data structure to contain data as follows:
    #   quarter-year
    #       territory
    #           download
    #           upload
    #           latency
    #           tests
    #           devices
    stats = {}
    # Get the list of territories
    territory_quadkeys = read_territory_quadkeys()
    print("Loaded", len(territory_quadkeys), "territories.")

    # For each file (for each Quarter) (multiquarter not implemented yet)
    stats.update({quarter_year: {}})
    # Get the file
    tile_url = get_tile_url("fixed", year, quarter)
    print("Downloading ", tile_url)
    # Now we need to read the geodata file from the url. However, if we are just testing, we can read from a local file.
    if testing:
        all_tiles = gp.read_file('ookla-test-data.zip')
    else:
        all_tiles = gp.read_file(tile_url)
    print("Downloaded ", len(all_tiles), "tiles.")
    
    # Process into tiles
    #   For each territory
    for territory in territory_quadkeys:
        print("Processing territory", territory)
        stats[quarter_year].update({territory: {}}) 
        print(stats)
        #     Filter into smaller tiles. To do this, we filter all_tiles for any that start with any of the territory's quadkeys.
        territory_tiles = all_tiles[all_tiles['quadkey'].str.startswith(tuple(territory_quadkeys[territory]))]
        #     Get statistics
        download = (territory_tiles['avg_d_kbps'].mean()) / 1000
        upload = (territory_tiles['avg_u_kbps'].mean()) / 1000
        latency = (territory_tiles['avg_lat_ms'].mean())
        tests = (territory_tiles['tests']).sum()
        devices = (territory_tiles['devices'].sum())
        print(f'{territory} {year}Q{quarter} Stats...\n Download (mean Mbps) {download}\n Upload (mean Mbps) {upload}\n Latency (mean ms) {latency}\n Tests {tests} Devices {devices}\n')
        #     add to stats data structure
        stats[quarter_year][territory].update({'download': download, 'upload': upload, 'latency': latency, 'tests': tests, 'devices': devices})
        #     Write territory_tiles to new file in geojson-datasets. This can be used for thing like mapping.
        #     Filename should be {territory}_ookla_{year}Q{quarter}.geojson
        geojson_filename = f'{directory}/{territory}_ookla_{year}Q{quarter}.geojson'
        territory_tiles.to_file(geojson_filename, driver='GeoJSON')
    # End for each territory
    # End for each file (not implemented yet)
    
    #     Write statistics to new stats file
    filename = f'{directory}/stats.json'
    with open(filename, 'w') as f:
        json.dump(stats, f, cls=NpEncoder)
    # close file
    f.close()
    # print finished timestamp
    print("Batch finished at", datetime.now())


if __name__ == '__main__':
    main()