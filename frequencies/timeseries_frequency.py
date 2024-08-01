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

def plot_frequency_data(df, title='Frequency Power Time Series'):
    plt.figure(figsize=(10, 6))
    plt.plot(df['Timestamp'], df['Power'], linestyle='-', color='blue')
    plt.title(title)
    plt.xlabel('Timestamp')
    plt.ylabel('Power (dB)')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# Parameters
base_folder = '/mnt/4tbssd/time_series_matrix_data/sh2'  # Replace with your base folder path
start_date = datetime(2018, 1, 1)  # Replace with your start date
end_date = datetime(2024, 7, 28)  # Replace with your end date
target_frequency = 2.4577  # Replace with the desired frequency in GHz

# Extract the data
time_series_data = extract_frequency_data(base_folder, start_date, end_date, target_frequency)

# Save to a CSV file
#time_series_data.to_csv('frequency_time_series.csv', index=False)

# Plot the data
plot_frequency_data(time_series_data, title=f'SH2_DSL, {target_frequency} GHz, Power (dBm), 20180101-20240728')
