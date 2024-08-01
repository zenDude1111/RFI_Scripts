import os
import pandas as pd
import numpy as np

# Define constants
input_path = "/mnt/4tbssd/time_series_matrix_data/sh1/old/2018"
output_path = "/mnt/4tbssd/time_series_matrix_data/sh1/2018"

# Ensure the output path exists
os.makedirs(output_path, exist_ok=True)

# Function to process and aggregate data
def process_file(file_path, output_path):
    # Read the CSV file
    data = pd.read_csv(file_path, index_col='Frequency (GHz)')

    # Ensure timestamps are sorted
    sorted_data = data.sort_index(axis=1)

    # Aggregate every 128 frequency channels by taking the max value
    freq_aggregated_data = sorted_data.groupby(np.arange(len(sorted_data)) // 128).max()
    freq_aggregated_data.index = sorted_data.index[::128][:len(freq_aggregated_data)]

    # Aggregate every 16 time columns by taking the max value
    time_columns = sorted_data.columns
    time_aggregated_data = pd.DataFrame(index=freq_aggregated_data.index)
    for i in range(0, len(time_columns), 16):
        max_values = freq_aggregated_data.iloc[:, i:i+16].max(axis=1)
        time_aggregated_data[time_columns[i]] = max_values

    # Save the aggregated data to the output path
    output_file_path = os.path.join(output_path, os.path.basename(file_path))
    time_aggregated_data.to_csv(output_file_path)

# Main script
n = 0  # Initialize the counter
for filename in os.listdir(input_path):
    if filename.endswith("matrix.csv"):
        input_file_path = os.path.join(input_path, filename)
        process_file(input_file_path, output_path)
        n += 1
        print(f"Processed file: {filename}, total processed: {n}")

print(f"Aggregation complete. Total files processed: {n}")

