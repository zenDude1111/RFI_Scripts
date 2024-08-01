import os
import pandas as pd
import numpy as np
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# Define constants
path = "/mnt/4tbssd/time_series_matrix_data/sh1/2021"
bucket = "test"
org = "barronlab"
token = "YRSeyxYPuw5LCKM7jPlNZekygOCrmkXko_5PeaweuldBixiAIpNec55qRicsnkCO4oP__0EX6crBukLj13uHlw=="
url = "http://universe.phys.unm.edu:8086"

# Initialize InfluxDB client
client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)

# Function to process and aggregate data
def process_file(file_path):
    data = pd.read_csv(file_path, index_col='Frequency (GHz)')

    # Ensure timestamps are sorted
    sorted_data = data.sort_index(axis=1)

    # Aggregate every 128 frequency channels by taking the max value
    aggregated_data = sorted_data.groupby(np.arange(len(sorted_data)) // 128).max()

    # Update the frequency index to reflect the aggregated intervals
    freq_index = np.linspace(data.index.min(), data.index.max(), len(aggregated_data))
    aggregated_data.index = freq_index

    return aggregated_data, sorted_data.columns

# Function to write data to InfluxDB
def write_to_influxdb(data, timestamps, date):
    for freq, row in data.iterrows():
        for time, value in zip(timestamps, row):
            # Combine date and time into ISO 8601 format
            datetime_str = f"{date}T{time}"
            # Create a point for InfluxDB
            point = Point("power_values") \
                .tag("frequency", freq) \
                .field("value", value) \
                .time(datetime_str)
            # Write the point to InfluxDB
            write_api.write(bucket=bucket, org=org, record=point)

# Main script
for filename in os.listdir(path):
    if filename.endswith("_matrix.csv"):
        file_path = os.path.join(path, filename)
        date = filename.split('_')[0]  # Extract date from filename
        data, timestamps = process_file(file_path)
        write_to_influxdb(data, timestamps, date)

# Close the InfluxDB client
client.close()
