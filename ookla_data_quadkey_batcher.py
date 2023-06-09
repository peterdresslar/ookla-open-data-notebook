# This script is a batcher that will process internet speed test files in the Ookla Open Data respository and filter out data for geographic areas of interest.
# The Ookla Open Data repository is described here: https://registry.opendata.aws/speedtest-global-performance/
# Ookla data is organized by one calendar quarter per file.
# It will process the file(s) into a set of internet speed statistics for each location, and save the statistics to a file.
# Then a geojson file is saved (in the folder geojson-datasets) for each quarter-year, for each location. This file can be used for mapping and visualization.
# Locations are defined for our purpose their quadkeys (more info here: https://docs.microsoft.com/en-us/bingmaps/articles/bing-maps-tile-system).
# We are focused on American islands and insular areas (territories) in this script, but it would be straightforward to modify this script to process other areas.
# Our locations are defined in the file island_quadkeys.json.
# For this script, we focus only on fixed internet service. It would be straightforward to modify this script to process mobile data.
#
# This script processes large files, and geopandas is memory intensive. Expect processing to take many minutes per file in most desktop environments.

# The stats data structure is as follows:
#   quarter-year
#       territory
#           download
#           upload
#           latency
#           tests
#           devices

import geopandas as gp
import numpy as np

import json
from datetime import datetime

# Create a quick numpy encoder so we can serialize our statistics to a file
# See: https://stackoverflow.com/a/57915246
# Todo move to a utils file
class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

# These are constants, the start year and quarter of available Ookla data in the repository.
ookla_data_start_year = 2019
ookla_data_start_quarter = 1

# Set this to true if you want to test the script without downloading the Ookla files (but instead use test data produced by ookla-test-data-creator.py)
testing = False

# Directory where the output files will be saved
directory = "geojson-datasets"

# Set the years and quarters to process. This could all be paramaterized, yes.
start_year = ookla_data_start_year
start_quarter = ookla_data_start_quarter
end_year = 2023
end_quarter = 2

def make_quarters_list() -> list:
    # Create a list of quarters to process
    quarters = []
    for year in range(start_year, end_year + 1):
        for q in range(1, 5):
            if year == start_year and q < start_quarter:
                continue
            if year == end_year and q > end_quarter:
                continue
            quarters.append((year, q))
    return quarters

def read_quadkeys() -> dict:
    # Read the list of territories from the file island_quadkeys.json
    # Any json file with locations and quadkeys should work here
    with open("island_quadkeys.json") as f:
        location_quadkeys = json.load(f)
    return location_quadkeys


def quarter_start(year: int, q: int) -> datetime:
    if not 1 <= q <= 4:
        raise ValueError("Quarter must be within [1, 2, 3, 4]")

    month = [1, 4, 7, 10]
    return datetime(year, month[q - 1], 1)


def get_tile_url(service_type: str, year: int, q: int) -> str:
    dt = quarter_start(year, q)
    base_url = (
        "https://ookla-open-data.s3-us-west-2.amazonaws.com/shapefiles/performance"
    )
    url = f"{base_url}/type%3D{service_type}/year%3D{dt:%Y}/quarter%3D{q}/{dt:%Y-%m-%d}_performance_{service_type}_tiles.zip"
    return url


def main():
    # print batch timestamp
    print("Batch started at", datetime.now())
    # Initialize the stats data structure, for all quarters, for all locations
    stats = {}
    # Get the list of quarters to process
    quarters = make_quarters_list()
    print("Processing", len(quarters), "quarters.")
    # Get the list of quadkey-locations
    location_quadkeys = read_quadkeys()
    print("Loaded", len(location_quadkeys), "locations.")

    # Everything is initialized, now we can start processing
    # For each quarter
    for year, quarter in quarters:
        #Save start time to calculate processing time
        start_time = datetime.now()
        quarter_year = str(year) + "Q" + str(quarter)
        print("Processing quarter", quarter_year)
        # For each file (for each Quarter) (multiquarter not implemented yet)
        stats.update({quarter_year: {}})
        # Get the file
        tile_url = get_tile_url("fixed", year, quarter)
        print("Downloading ", tile_url)
        # Now we need to read the geodata file from the url. However, if we are just testing, we can read from a local file.
        if testing:
            all_tiles = gp.read_file("ookla-test-data.zip")
        else:
            all_tiles = gp.read_file(tile_url)
        print("Downloaded ", len(all_tiles), "tiles.")

        # Process into tiles
        #   For each territory
        for location in location_quadkeys:
            print("Processing location", location)
            stats[quarter_year].update({location: {}})
            #     Filter into smaller tiles. To do this, we filter all_tiles for any that start with any of the territory's quadkeys.
            location_tiles = all_tiles[
                all_tiles["quadkey"].str.startswith(tuple(location_quadkeys[location]))
            ]
            #     Get statistics
            download = (location_tiles["avg_d_kbps"].mean()) / 1000
            upload = (location_tiles["avg_u_kbps"].mean()) / 1000
            latency = location_tiles["avg_lat_ms"].mean()
            tests = (location_tiles["tests"]).sum()
            devices = location_tiles["devices"].sum()
            print(
                f"{location} {year}Q{quarter} Stats...\n Download (mean Mbps) {download}\n Upload (mean Mbps) {upload}\n Latency (mean ms) {latency}\n Tests {tests} Devices {devices}\n"
            )
            #     Add to stats data structure
            stats[quarter_year][location].update(
                {
                    "download": download,
                    "upload": upload,
                    "latency": latency,
                    "tests": tests,
                    "devices": devices,
                }
            )
            #     Write location_tiles to new file in geojson-datasets.
            #     Filename should be {location}_ookla_{year}Q{quarter}.geojson
            geojson_filename = f"{directory}/{location}_ookla_{year}Q{quarter}.geojson"
            location_tiles.to_file(geojson_filename, driver="GeoJSON")
            # End for each location
        # Calculate processing time
        end_time = datetime.now()
        processing_time = end_time - start_time
        print("Processing time for quarter", quarter_year, "was", processing_time)
        # End for each quarter

    #     Write all statistics to new stats file
    filename = f"{directory}/stats.json"
    with open(filename, "w") as f:
        json.dump(stats, f, cls=NpEncoder)
    # close file
    f.close()
    # print finished timestamp
    print("Batch finished at", datetime.now())


if __name__ == "__main__":
    main()
