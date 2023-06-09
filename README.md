# ookla-open-data-notebook

This repo was built by Pacific Broadband and Digital Equity (https://pacificbroadband.org) to explore ookla-open-data speeds specific to the United States Pacific territories. 

## Updates, 2023-07-09

(`ookla_data_quadkey_batcher.py`) 

Major changes in the form of "batchifying" the original notebook mean that we can now grab and process much more data. As a result we are able to generate more statistics, and we have added a facility to save these to a json file (`geodatasets\stats.json`). This file has the following format:

* quarter-year
  * territory
    * download
    * upload
    * latency
    * tests
    * devices

We are now processing all islands of Hawaii, most USA island Insular Areas, and the Azore islands for reference.

We have run `ookla_data_quadkey_batcher.py` on Python 3 on a fairly basic Windows machine successfully. With limited memory, processing can take a few hours at least.

We also added `ookla_test_data_creator.py` to help aid development by simulating an ookla-open-data file with just 100 tiles. It is much faster to develop and test with.

## The Notebook

(`notebook\ookla-open-data-notebook.ipynb`)

The beginning of the notebook in particular borrows from the tutorials at https://github.com/teamookla/ookla-open-data. Parsing out the data from millions and millions of quarterly speed reports into small slices takes significant time, especially just to read the data into a geopandas dataframe. 

The Ookla data include quadkeys, a geographic organization system described here: (https://learn.microsoft.com/en-us/bingmaps/articles/bing-maps-tile-system). Quadkeys can be used to identify specific areas on Earth, and this notebook uses quadkeys to isolate individual test records for a given area. In this case, we have included sample quadkeys for all the United States territories and Hawaii, but other locations with other quadkeys could easily be substituted.

Once that is done, this notebook generates an output geojson file (the format of which could easily be switched) and a data summary to text, like this: (note this is now automated by the batcher script)

`guam 2022Q3 Stats... Download (mean Mbps) 46.69761086956522 Upload (mean Mbps) 6.610093478260869 Latency (mean ms) 19.080434782608695 Tests 8612 Devices 2908`

Geojson can be uploaded into a variety of systems, including Mapbox:

![Map image](image.png)

The repo contains sample data downloaded for various locations in the Pacific. Other locations could easily be processed with the notebook. Conversion of the notebook to an operational service would be straightforward, but the geopandas file loading bottleneck would need to be considered for that work.  

### Citation

Speedtest by Ookla Global Fixed and Mobile Network Performance Maps was accessed on [variable dates] from https://registry.opendata.aws/speedtest-global-performance. Speedtest® by Ookla® Global Fixed and Mobile Network Performance Maps. Based on analysis by Ookla of Speedtest Intelligence® data for [variable period]. Provided by Ookla and accessed [day accessed]. Ookla trademarks used under license and reprinted with permission.