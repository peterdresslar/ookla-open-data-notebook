# This script grabs an arbitrary Ookla (fixed) file from the Ookla-open-data Amazon S3 bucket, and processes it into a
# small zipped file with the first 100 tiles (or less) that match the selected quadkey (in this case, we use an arbitrary quadkey from where I live). 
# The file can be used for testing and development. Adjust as desired.
# The ookla files are pretty big, so this script can take a while to run depending on your processing environment.

import geopandas as gp
import pandas as pd
import numpy as np
import json
import os
import shutil

from shapely.geometry import Point
from adjustText import adjust_text

from datetime import datetime

# Set our quadkey
arbitrary_quadkey = "02221111"

# Create a temporary directory
temp_dir = "temp"
if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir)
os.mkdir(temp_dir)

# Get the file and read into a geopandas dataframe
# tile_url = "https://ookla-open-data.s3-us-west-2.amazonaws.com/shapefiles/performance/type%3Dfixed/year%3D2021/quarter%3D1/2021-01-01_performance_fixed_tiles.zip"
# print("Reading file ", tile_url)
# tiles = gp.read_file(tile_url)
# print("Read ", len(tiles), "tiles.")

# Get the first 100 tiles that match the quadkey
#print("Getting first 100 tiles that match quadkey ", arbitrary_quadkey)
#tiles = tiles[tiles['quadkey'].str.startswith(arbitrary_quadkey)]
#tiles = tiles.head(100)
#print("Got ", len(tiles), "tiles.")

# Write the file to a temporary directory
print("Writing file to temporary directory")
#tiles.to_file(temp_dir, driver='GeoJSON')
# write a test file to the temp directory with just the line "test"
with open(temp_dir + "/test.txt", "w") as f:
    f.write("test")
# close the file
f.close()
# Zip the file
print("Zipping file")
shutil.make_archive("ookla-test-data", 'zip', temp_dir)

# Print the file size
print("File size is ", os.path.getsize("ookla-test-data.zip"), "bytes")

# Delete the temporary directory
print("Deleting temporary directory")
shutil.rmtree(temp_dir)

# And we're done!

