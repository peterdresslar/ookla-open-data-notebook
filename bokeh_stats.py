# This script processes the stats.json file created by ookla_data_quadkey_batcher.py and creates a Bokeh visualization of the data
# as time series charts for Upload, Download, and Latency values.
#
# It can be called on its own or from the end of the batcher script.

# Note that this script assumes Python 3.6 or higher. Before running this script, you will need to install bokeh and pandas.

import argparse
import json

from bokeh.models import HoverTool, ColumnDataSource
from bokeh.palettes import Category10
from bokeh.plotting import figure, show, output_file

import pandas as pd

def generate_time_series_plot(data, title, y_axis_column, x_axis_label, y_axis_label, no_hawaii):
    # Define color groups
    color_groups = {
        'micronesia': Category10[10][0:4],  # Assign different colors for each group
        'hawaii': Category10[10][4:8],
        'carribean': Category10[10][8:],
        'us-and-atlantic': ['black', 'grey']
    }

    # Count groups for assigning colors
    group_counts = {group: 0 for group in color_groups}

    # All the locations, grouped as Micronesia, Hawaii, Carribean, US-and-Atlantic
    location_groups = {
    'guam': 'micronesia',
    'cnmi': 'micronesia',
    'am-samoa': 'micronesia',
    'palau-all': 'micronesia',
    'fsm': 'micronesia',
    'usvi': 'carribean',
    'pr': 'carribean',
    'oahu': 'hawaii',
    'maui': 'hawaii',
    'niihau': 'hawaii',
    'kauai': 'hawaii',
    'molokai': 'hawaii',
    'lanai': 'hawaii',
    'kahoolawe': 'hawaii',
    'hawaii-island': 'hawaii',
    'hawaii-state': 'hawaii',
    'bozeman-mt': 'us-and-atlantic',
    'azores': 'us-and-atlantic',
    }

    # Don't break out hawaii islands...
    location_groups_no_hawaii_islands = {
    'guam': 'micronesia',
    'cnmi': 'micronesia',
    'am-samoa': 'micronesia',
    'palau-all': 'micronesia',
    'fsm': 'micronesia',
    'usvi': 'carribean',
    'pr': 'carribean',
    'hawaii-state': 'hawaii',
    'bozeman-mt': 'us-and-atlantic',
    'azores': 'us-and-atlantic',
    }

    # Use the no_hawaii flag to determine which location groups to use
    if no_hawaii:
        location_groups = location_groups_no_hawaii_islands

    # Create a Bokeh plot
    p = figure(title=title, x_axis_label=x_axis_label, y_axis_label=y_axis_label, x_axis_type='datetime', width=800, height=600)

    # Iterate over locations based on the predefined order in location_groups
    for location in location_groups.keys():
        if location in data['location'].unique():
            # Filter data for each location
            location_data = data[data['location'] == location]

            # Get the group and corresponding color
            group = location_groups[location]
            color = color_groups[group][group_counts[group] % len(color_groups[group])]
            group_counts[group] += 1  # Increment the count for this group

            # Create a ColumnDataSource
            source = ColumnDataSource(location_data)

            # Plot line
            p.line('date', y_axis_column, source=source, legend_label=location, line_width=2, color=color)

            # Add Hover tool
            hover = HoverTool()
            hover.tooltips = [("Location", "@location"), (y_axis_label, f"@{y_axis_column}")]
            p.add_tools(hover)

    # Move legend to the left and make it interactive
    p.legend.location = "top_left"
    p.legend.click_policy = "hide"

    return p

def plot_3(df, no_hawaii=False):

    # Assuming 'data' is your DataFrame
    plot_download = generate_time_series_plot(df, "Internet Download Speed Over Time", "download", "Date", "Download Speed (Mbps)", no_hawaii)
    plot_upload = generate_time_series_plot(df, "Internet Upload Speed Over Time", "upload", "Date", "Upload Speed (Mbps)", no_hawaii)
    plot_latency = generate_time_series_plot(df, "Internet Latency Over Time", "latency", "Date", "Latency (ms)", no_hawaii)

    # Output the plots to HTML files
    output_file("internet_download_speeds.html")
    show(plot_download)

    output_file("internet_upload_speeds.html")
    show(plot_upload)

    output_file("internet_latency.html")
    show(plot_latency)

if __name__ == "__main__":
    # Check args for "no-hawaii-islands" flag. In this case we will not plot those.
    # Create the parser
    parser = argparse.ArgumentParser(description='Plot Data')
    
    # Add the arguments
    parser.add_argument('--no-hawaii-islands', action='store_true', help='Do not plot Hawaii Islands.')

    # Parse the arguments
    args = parser.parse_args()
    no_hawaii_islands = args.no_hawaii_islands

    print(f"Plotting data for Hawaii Islands: {not no_hawaii_islands}")

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
    plot_3(df, no_hawaii_islands)
