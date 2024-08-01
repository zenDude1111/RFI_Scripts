import os
import requests
import tarfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import glob
from scipy.stats import skew, kurtosis
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor
import re

# Define constants
URL = "http://bicep.rc.fas.harvard.edu/southpole_info/EMI_WG/keckdaq/signalhound2/"
SAVE_DIR = '/mnt/4tbssd/raw_data/sh2/'
AGG_MATRIX_DIR = "/mnt/4tbssd/time_series_matrix_data/sh2/2024"
METRICS_OUTPUT_DIR = '/mnt/4tbssd/daily_metrics/sh2/'
START_DATE_STR = '20240729'  # Example start date in YYYYMMDD format
CHUNK_SIZE = 1000

# Ensure necessary directories exist
os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs(AGG_MATRIX_DIR, exist_ok=True)
os.makedirs(METRICS_OUTPUT_DIR, exist_ok=True)

# Functions for downloading and unpacking
def download_file(url, path):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        total_size_in_bytes = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 Kibibyte

        with open(path, 'wb') as file:
            for data in response.iter_content(block_size):
                file.write(data)
        print(f"Download completed for {path}")
    except requests.RequestException as e:
        print(f"Error downloading {url}: {e}")
        if os.path.exists(path):
            os.remove(path)

def unpack_and_delete_tar(tar_path, save_directory):
    try:
        print(f"Unpacking {tar_path}...")
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=save_directory)
        print(f"Unpacked {tar_path}")
    except tarfile.TarError as e:
        print(f"Error unpacking {tar_path}: {e}")
    finally:
        if os.path.exists(tar_path):
            os.remove(tar_path)
            print(f"Deleted {tar_path}")

def download_and_process(url, link, save_directory):
    tar_path = os.path.join(save_directory, link)
    download_file(url + link, tar_path)
    unpack_and_delete_tar(tar_path, save_directory)

def download_and_unpack_tar(url, save_directory, start_date_str):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        tar_links = [a['href'] for a in soup.find_all('a') if a['href'].endswith('.tar.gz')]
    except requests.RequestException as e:
        print(f"Error retrieving URL {url}: {e}")
        return

    start_date = datetime.strptime(start_date_str, '%Y%m%d')

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for link in tar_links:
            try:
                file_date = datetime.strptime(link[:8], '%Y%m%d')
                if file_date >= start_date:
                    futures.append(executor.submit(download_and_process, url, link, save_directory))
            except ValueError:
                continue

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error in concurrent processing: {e}")

# Functions for processing data into aggregated matrices
def convert_power_mw_to_dbm(power_mw):
    return 10 * np.log10(power_mw)

def process_file(file_path):
    try:
        file_name = os.path.basename(file_path)
        timestamp = datetime.strptime(file_name.split('_')[1], '%H%M%S').strftime('%H:%M:%S')
        df = pd.read_csv(file_path, usecols=[0, 1], names=['Frequency (MHz)', 'Amplitude Min(mW)'], skiprows=1)
        df['Frequency (GHz)'] = (df['Frequency (MHz)'] / 1000).round(4)
        df['Power (dBm)'] = convert_power_mw_to_dbm(df['Amplitude Min(mW)'])
        df['Timestamp'] = timestamp
        return df[['Frequency (GHz)', 'Timestamp', 'Power (dBm)']]
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return pd.DataFrame()

def reshape_data(all_data):
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        pivot_df = combined_df.pivot_table(index='Frequency (GHz)', columns='Timestamp', values='Power (dBm)', aggfunc='mean').reset_index()
        pivot_df.columns.name = None
        
        freq_aggregated_data = pivot_df.groupby(np.arange(len(pivot_df)) // 128).max()
        freq_aggregated_data.index = pivot_df['Frequency (GHz)'].iloc[::128][:len(freq_aggregated_data)]

        time_columns = freq_aggregated_data.columns[1:]
        time_aggregated_data = pd.DataFrame(index=freq_aggregated_data.index)
        time_aggregated_data['Frequency (GHz)'] = freq_aggregated_data.index
        for i in range(0, len(time_columns), 16):
            max_values = freq_aggregated_data.iloc[:, i+1:i+17].max(axis=1)
            time_aggregated_data[time_columns[i]] = max_values

        return time_aggregated_data
    else:
        return pd.DataFrame()

def process_day_directory(day_directory_path, output_directory):
    all_data = []
    file_paths = glob.glob(os.path.join(day_directory_path, '*_trace.csv'))

    for file_path in file_paths:
        df = process_file(file_path)
        if not df.empty:
            all_data.append(df)

    final_df = reshape_data(all_data)
    day_directory = os.path.normpath(day_directory_path)
    day = os.path.basename(day_directory)
    
    if not final_df.empty:
        output_file = os.path.join(output_directory, f'{day}_matrix.csv')
        final_df.to_csv(output_file, index=False)
        print(f"Matrix for {day} saved to {output_file}")
    else:
        print(f"No data processed for {day}.")

def process_all_days(input_directory, output_directory, start_date_str):
    start_date = datetime.strptime(start_date_str, '%Y%m%d')
    day_directories = glob.glob(os.path.join(input_directory, '*/'))

    day_directories.sort(key=lambda x: datetime.strptime(os.path.basename(os.path.normpath(x)), '%Y%m%d'))

    for day_directory in day_directories:
        day = os.path.basename(os.path.normpath(day_directory))
        day_date = datetime.strptime(day, '%Y%m%d')
        if day_date >= start_date:
            process_day_directory(day_directory, output_directory)

# Functions for calculating metrics
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

def process_files_from_start_date(base_directory_path, start_date_str):
    start_date = datetime.strptime(start_date_str, '%Y%m%d')
    for input_file_path in glob.glob(f'{base_directory_path}/**/*_matrix.csv', recursive=True):
        file_date_str = os.path.basename(input_file_path).split('_')[0]
        file_date = datetime.strptime(file_date_str, '%Y%m%d')
        if file_date >= start_date:
            df = pd.read_csv(input_file_path)
            summary_df = parallel_process(df, CHUNK_SIZE)
            summary_df.sort_values(by='Frequency (GHz)', inplace=True)

            output_summary_path = os.path.join(METRICS_OUTPUT_DIR, f'{file_date_str}_metrics.csv')
            summary_df.to_csv(output_summary_path, index=False)
            print(f'Summary statistics written to {output_summary_path}')

# Main script execution
def main():
    download_and_unpack_tar(URL, SAVE_DIR, START_DATE_STR)
    process_all_days(SAVE_DIR, AGG_MATRIX_DIR, START_DATE_STR)
    process_files_from_start_date(AGG_MATRIX_DIR, START_DATE_STR)

if __name__ == "__main__":
    main()
