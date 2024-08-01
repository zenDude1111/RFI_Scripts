import pandas as pd
from scipy.stats import skew, kurtosis
import numpy as np
import os
import glob
from concurrent.futures import ProcessPoolExecutor
import concurrent.futures
import re

# Define base directory paths
base_directory_path = '/mnt/4tbssd/time_series_matrix_data/sh1/'
output_base_path = '/mnt/4tbssd/daily_metrics/sh1'

# Ensure the output base path exists
os.makedirs(output_base_path, exist_ok=True)

# Define function for statistical calculations
def process_chunk(chunk):
    frequencies = chunk['Frequency (GHz)']
    numeric_chunk = chunk.drop(columns=['Frequency (GHz)'])
    stats = {
        'Mean (dBm)': numeric_chunk.mean(axis=1).round(4),
        'Median (dBm)': numeric_chunk.median(axis=1).round(4),
        'Min (dBm)': numeric_chunk.min(axis=1).round(4),
        'Max (dBm)': numeric_chunk.max(axis=1).round(4),
        'Skew': skew(numeric_chunk, axis=1).round(4),
        'Kurtosis': kurtosis(numeric_chunk, axis=1).round(4)
    }
    result_df = pd.DataFrame(stats)
    result_df.insert(0, 'Frequency (GHz)', frequencies.values)
    return result_df

def parallel_process(df, chunk_size):
    chunks = [df.iloc[i:i + chunk_size] for i in range(0, df.shape[0], chunk_size)]
    results = []
    with ProcessPoolExecutor() as executor:
        future_to_chunk = {executor.submit(process_chunk, chunk): chunk for chunk in chunks}
        for future in concurrent.futures.as_completed(future_to_chunk):
            results.append(future.result())
    final_df = pd.concat(results, ignore_index=True)
    return final_df

# Function to extract year from file path
def extract_year(file_path):
    match = re.search(r'/(\d{4})/', file_path)
    if match:
        return int(match.group(1))
    return None

# Main processing loop with date range filtering
def process_files_in_date_range(start_year, end_year):
    for input_file_path in glob.glob(f'{base_directory_path}/**/*_matrix.csv', recursive=True):
        year = extract_year(input_file_path)
        if year is not None and start_year <= year <= end_year:
            df = pd.read_csv(input_file_path)
            summary_df = parallel_process(df, chunk_size=1000)
            summary_df.sort_values(by='Frequency (GHz)', inplace=True)

            # Extracting date from the input file path
            date_part = os.path.basename(input_file_path).split('_')[0]
            output_summary_path = os.path.join(output_base_path, f'{date_part}_metrics.csv')

            summary_df.to_csv(output_summary_path, index=False)
            print(f'Summary statistics written to {output_summary_path}')

# Example usage
start_year = 2018
end_year = 2025
process_files_in_date_range(start_year, end_year)
