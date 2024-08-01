import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

def extract_frequency_data(base_folder, start_date, end_date, target_frequency):
    all_data = []
    
    for year_folder in os.listdir(base_folder):
        year_folder_path = os.path.join(base_folder, year_folder)
        
        if os.path.isdir(year_folder_path):
            for csv_file in os.listdir(year_folder_path):
                try:
                    # Extract the date from the file name
                    file_date_str = csv_file.split('_')[0]
                    file_date = datetime.strptime(file_date_str, '%Y%m%d')
                except ValueError:
                    # Skip files that don't match the expected date format
                    continue
                
                # Check if the file is within the specified date range
                if start_date <= file_date <= end_date:
                    file_path = os.path.join(year_folder_path, csv_file)
                    df = pd.read_csv(file_path)
                    
                    # Filter the row with the desired frequency
                    frequency_row = df[df['Frequency (GHz)'] == target_frequency]
                    
                    if not frequency_row.empty:
                        frequency_data = frequency_row.iloc[0, 1:]  # Skip the first column (Frequency)
                        # Combine date and time to form a full timestamp
                        timestamps = [datetime.combine(file_date, datetime.strptime(t, '%H:%M:%S').time()) 
                                      for t in frequency_data.index]
                        power_values = frequency_data.values
                        
                        # Store the data with timestamps
                        all_data.extend(zip(timestamps, power_values))
    
    # Create a DataFrame from the collected data and sort by timestamp
    time_series_df = pd.DataFrame(all_data, columns=['Timestamp', 'Power'])
    time_series_df = time_series_df.sort_values(by='Timestamp').reset_index(drop=True)
    
    return time_series_df

def plot_frequency_data(df, frequency, output_dir):
    plt.figure(figsize=(14, 6))
    plt.plot(df['Timestamp'], df['Power'], linestyle='-', color='blue')
    plt.title(f'SH2-DSL, {frequency} GHz, Power (dBm)')
    plt.xlabel('Timestamp')
    plt.ylabel('Power (dBm)')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    output_file = os.path.join(output_dir, f'{frequency}GHz.png')
    plt.savefig(output_file)
    plt.close()

def process_frequencies(base_folder, start_date, end_date, output_dir):
    # Iterate over each file to get the list of frequencies
    sample_file = os.path.join(base_folder, os.listdir(base_folder)[0], os.listdir(os.path.join(base_folder, os.listdir(base_folder)[0]))[0])
    df_sample = pd.read_csv(sample_file)
    frequencies = df_sample['Frequency (GHz)'].unique()

    for frequency in frequencies:
        print(f'Processing frequency: {frequency} GHz')
        data = extract_frequency_data(base_folder, start_date, end_date, frequency)
        plot_frequency_data(data, frequency, output_dir)

# Parameters
base_folder = '/mnt/4tbssd/time_series_matrix_data/sh2'  # Replace with your base folder path
start_date = datetime(2018, 1, 1)  # Replace with your start date
end_date = datetime(2024, 7, 28)  # Replace with your end date
output_dir = '/home/polarbear/Desktop/erics_code/frequency_analysis/sh2_all'  # Directory to save plots

# Ensure the output directory exists
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Process each frequency one by one
process_frequencies(base_folder, start_date, end_date, output_dir)
