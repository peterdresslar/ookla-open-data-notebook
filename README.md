# ookla-open-data-notebook

This workbook was built by Pacific Broadband and Digital Equity (https://pacificbroadband.org) to explore ookla-open-data speeds specific to the United States Pacific territories. The beginning of the workbook in particular borrows from the tutorials at https://github.com/teamookla/ookla-open-data. Parsing out the data from millions and millions of quarterly speed reports into small slices takes significant time, especially just to read the data into a geopandas dataframe. 

Once that is done, this workbook generates an output geojson file (the format of which could easily be switched) and a data summary to text. Geojson can be uploaded into a variety of systems, including Mapbox:

![Map image](image.png)

Special thanks to Tyrone Taitano and Government of Guam for their support of the work.
