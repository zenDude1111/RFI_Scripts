import numpy as np
import pandas as pd
import os
import re

# Specify the directory containing the .npz files and the output directory for CSV files
input_directory = '/mnt/4tbssd/southpole_rfi_data/anritsu/'
output_directory = '/mnt/4tbssd/time_series_matrix_data/anritsu/2024/'

def format_timestamps(timestamps):
    # Convert timestamps to datetime objects and format them as HH:MM:SS
    formatted_timestamps = [pd.to_datetime(ts).strftime('%H:%M:%S') for ts in timestamps]
    return formatted_timestamps

# Ensure the output directory exists
os.makedirs(output_directory, exist_ok=True)

# Regular expression to extract date from the filename
date_pattern = re.compile(r'(\d{4}-\d{2}-\d{2})T')

# Process each .npz file in the input directory
for filename in os.listdir(input_directory):
    if filename.endswith('.npz'):
        file_path = os.path.join(input_directory, filename)
        
        # Extract the date from the filename
        match = date_pattern.search(filename)
        if match:
            date_str = match.group(1).replace('-', '')
            output_csv_path = os.path.join(output_directory, f'{date_str}_matrix.csv')
        else:
            print(f"Date not found in filename: {filename}")
            continue
        
        try:
            # Load the .npz file
            data = np.load(file_path)
            
            # Extract the frequencies, timestamps, and data arrays
            frequencies = data['frequencies']
            timestamps = data['timestamps']
            data_values = data['data']
            
            # Transpose the data array to match the dimensions
            data_values = data_values.T
            
            # Format the timestamps
            formatted_timestamps = format_timestamps(timestamps)
            
            # Create a DataFrame with frequencies as the index and formatted timestamps as the columns
            df = pd.DataFrame(data=data_values, index=frequencies, columns=formatted_timestamps)
            
            # Set the index name for clarity
            df.index.name = 'Frequency (GHz)'
            
            # Save the DataFrame to a CSV file with the desired format
            df.to_csv(output_csv_path, index=True, float_format='%.14f')
            
            print(f"Matrix with frequencies on y-axis and formatted timestamps on x-axis saved to {output_csv_path}")
                
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except Exception as e:
            print(f"An error occurred while processing {file_path}: {e}")







