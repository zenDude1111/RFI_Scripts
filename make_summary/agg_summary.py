import pandas as pd
import numpy as np
import os
import glob
from concurrent.futures import ProcessPoolExecutor
import concurrent.futures
import re

# Define base directory paths
base_directory_path = '/media/polarbear/586CF6E16CF6B8B8/sh2/'
output_base_path = '/mnt/4tbssd/day_reports/sh2'

# Ensure the output base path exists
os.makedirs(output_base_path, exist_ok=True)

# Function to process and aggregate data
def process_chunk(chunk):
    frequencies = chunk['Frequency (GHz)']
    numeric_chunk = chunk.drop(columns=['Frequency (GHz)'])

    # Aggregate every 128 frequency channels by taking the max value
    freq_aggregated_data = numeric_chunk.groupby(np.arange(len(numeric_chunk)) // 128).max()
    freq_aggregated_data.index = frequencies.iloc[::128][:len(freq_aggregated_data)]

    # Aggregate every 16 time columns by taking the max value
    time_columns = numeric_chunk.columns
    time_aggregated_data = pd.DataFrame(index=freq_aggregated_data.index)
    for i in range(0, len(time_columns), 16):
        max_values = freq_aggregated_data.iloc[:, i:i+16].max(axis=1)
        time_aggregated_data[time_columns[i]] = max_values

    # Creating a summary DataFrame
    stats = {
        'Power (dBm)': time_aggregated_data.max(axis=1)
    }
    result_df = pd.DataFrame(stats)
    result_df.insert(0, 'Frequency (GHz)', freq_aggregated_data.index)

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
            output_summary_path = os.path.join(output_base_path, f'{date_part}_summary.csv')

            summary_df.to_csv(output_summary_path, index=False)
            print(f'Summary statistics written to {output_summary_path}')

# Example usage
start_year = 2020
end_year = 2020
process_files_in_date_range(start_year, end_year)

