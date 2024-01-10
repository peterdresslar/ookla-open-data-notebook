# This script processes the stats.json file created by ookla_data_quadkey_batcher.py and creates a Bokeh visualization of the data
# as time series charts for Upload, Download, and Latency values.
#
# It can be called on its own or from the end of the batcher script.

# Note that this script assumes Python 3.6 or higher. Before running this script, you will need to install bokeh and pandas.

import json

from bokeh.plotting import figure, show, output_file
from bokeh.models import HoverTool, ColumnDataSource
import pandas as pd


def generate_time_series_plot(data, title, y_axis_column, x_axis_label, y_axis_label):
    # Create a Bokeh plot
    p = figure(title=title, x_axis_label=x_axis_label, y_axis_label=y_axis_label, x_axis_type='datetime')

    # Iterate over locations
    for location in data['location'].unique():
        # Filter data for each location
        location_data = data[data['location'] == location]

        # Create a ColumnDataSource
        source = ColumnDataSource(location_data)

        # Plot line
        p.line('date', y_axis_column, source=source, legend_label=location, line_width=2)

        # Add Hover tool
        hover = HoverTool()
        hover.tooltips = [("Location", "@location"), (y_axis_label, f"@{y_axis_column}")]
        p.add_tools(hover)

        # Make legend interactive
        p.legend.click_policy = "hide"

    # Return one plot. Note that we are not calling show() here.
    return p

def plot_3(df):

    # Assuming 'data' is your DataFrame
    plot_download = generate_time_series_plot(df, "Internet Download Speed Over Time", "download", "Date", "Download Speed (Mbps)")
    plot_upload = generate_time_series_plot(df, "Internet Upload Speed Over Time", "upload", "Date", "Upload Speed (Mbps)")
    plot_latency = generate_time_series_plot(df, "Internet Latency Over Time", "latency", "Date", "Latency (ms)")

    # Output the plots to HTML files
    output_file("internet_download_speeds.html")
    show(plot_download)

    output_file("internet_upload_speeds.html")
    show(plot_upload)

    output_file("internet_latency.html")
    show(plot_latency)

if __name__ == "__main__":
    # Import data from stats.json
    path = "stats.json"

    with open(path, 'r') as f:
        data = json.load(f)

    rows = []
    for quarter, locations in data.items():
        for location, values in locations.items():
            rows.append([pd.to_datetime(quarter), location, values['download'], values['upload'], values['latency']])
    
    df = pd.DataFrame(rows, columns=['date', 'location', 'download', 'upload', 'latency'])
    print(df.head())

    # Now plot the three timeseries
    plot_3(df)
