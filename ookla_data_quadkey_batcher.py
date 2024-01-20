# This script is a batcher that will process internet speed test files in the Ookla Open Data respository and filter out data for geographic areas of interest.
# The Ookla Open Data repository is described here: https://registry.opendata.aws/speedtest-global-performance/
# Ookla data is organized by one calendar quarter per file.
# It will process the file(s) into a set of internet speed statistics for each location, and save the statistics to a file.
# Then a geojson file is saved (in the folder geojson-datasets) for each quarter-year, for each location. This file can be used for mapping and visualization.
# Locations are defined for our purpose their quadkeys (more info here: https://docs.microsoft.com/en-us/bingmaps/articles/bing-maps-tile-system).
# We are focused on American islands and insular areas (territories) in this script, but it would be straightforward to modify this script to process other areas.
# Our locations are defined in the file island_quadkeys.json.
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

# To run this script from the command line, use the following command:
# python ookla_data_quadkey_batcher.py
# Use the following arguments to specify the start and end quarters to process:
# --start_year (e.g., 2019)
# --start_quarter (e.g., 1)
# --end_year (e.g., 2020)
# --end_quarter (e.g., 2)
# Or you can use the defaults, which will process all available data based upon today's date.
# You can also specify whether to process mobile or fixed internet service data.
# --mobile will process mobile data, otherwise the script will process fixed internet service data.
# There are a couple of other arguments that are mostly for testing purposes; see the code below for details.
# Note that this script assumes Python 3.6 or higher. Before running this script, you will need to install geopandas and numpy.

import argparse
import json
import os
from datetime import datetime

import geopandas as gp
import numpy as np


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


# Directory where the output files will be saved
directory = "geojson-datasets"

# Set the years and quarters to process. The default is to process all available data using the constant start year and quarter, and the current date.
# Create the parser
parser = argparse.ArgumentParser(description="Process Ookla data.")

# These are constants, the start year and quarter of available Ookla data in the repository.
ookla_data_start_year = 2019
ookla_data_start_quarter = 1

# Get the current year and quarter
current_year = datetime.now().year
current_month = datetime.now().month
current_quarter = (current_month - 1) // 3 + 1

# Calculate the most recent year and quarter with available data
most_recent_year = current_year if current_quarter > 1 else current_year - 1
most_recent_quarter = current_quarter - 1 if current_quarter > 1 else 4

# Add the arguments
parser.add_argument(
    "--start_year",
    type=int,
    default=ookla_data_start_year,
    help="The start year to process.",
)
parser.add_argument(
    "--start_quarter",
    type=int,
    default=ookla_data_start_quarter,
    help="The start quarter to process.",
)
parser.add_argument(
    "--end_year", type=int, default=most_recent_year, help="The end year to process."
)
parser.add_argument(
    "--end_quarter",
    type=int,
    default=most_recent_quarter,
    help="The end quarter to process.",
)
parser.add_argument(
    "--mobile",
    action="store_true",
    help="Process mobile data instead of fixed internet service.",
)
parser.add_argument(
    "--preserve-stats",
    type=bool,
    default=True,
    help="Preserve existing stats.json file.",
)
parser.add_argument(
    "--testing", action="store_true", help="Use test data instead of Ookla data."
)

# Parse the arguments
args = parser.parse_args()

# Some args are constants
# start_year is args.start_year or ookla_data_start_year
start_year = args.start_year if args.start_year else ookla_data_start_year
# start_quarter is args.start_quarter or ookla_data_start_quarter
start_quarter = args.start_quarter if args.start_quarter else ookla_data_start_quarter
# end_year is args.end_year or most_recent_year
end_year = args.end_year if args.end_year else most_recent_year
# end_quarter is args.end_quarter or most_recent_quarter
end_quarter = args.end_quarter if args.end_quarter else most_recent_quarter

fixed_or_mobile = "mobile" if args.mobile else "fixed"

# Set the testing flag
testing = args.testing

# If preserve-stats is True and stats.json exists, load its contents into stats
if args.preserve_stats and os.path.exists("stats.json"):
    with open("stats.json", "r") as f:
        stats = json.load(f)
    print(f"Loaded stats for {len(stats)} quarters.")
# Otherwise, initialize stats as an empty dictionary
else:
    stats = {}


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
        # Save start time to calculate processing time
        start_time = datetime.now()
        quarter_year = str(year) + "Q" + str(quarter)
        print("Processing quarter", quarter_year)
        # For each file (for each Quarter) (multiquarter not implemented yet)
        stats.update({quarter_year: {}})
        # Get the file
        tile_url = get_tile_url(fixed_or_mobile, year, quarter)  # all set by args
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
            geojson_filename = f"{directory}/{fixed_or_mobile}/{location}_ookla_{year}Q{quarter}.geojson"
            location_tiles.to_file(geojson_filename, driver="GeoJSON")
            # End for each location
        # Calculate processing time
        end_time = datetime.now()
        processing_time = end_time - start_time
        print("Processing time for quarter", quarter_year, "was", processing_time)
        # End for each quarter

    #     Write all statistics to new stats file
    filename = f"stats.json"
    with open(filename, "w") as f:
        json.dump(stats, f, cls=NpEncoder)
    # close file
    f.close()
    # print finished timestamp
    print("Batch finished at", datetime.now())


if __name__ == "__main__":
    main()
