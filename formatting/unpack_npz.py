import numpy as np
import pandas as pd

# Specify the file path
file_path = '/mnt/4tbssd/anritsu/anritsu/dsl_2024-05-16T00-09.npz'
output_csv_path = '/mnt/4tbssd/time_series_matrix_data/anritsu/2024/20240516_matrix.csv'  # Output CSV file path

def format_timestamps(timestamps):
    # Convert timestamps to datetime objects and format them as HH:MM:SS
    formatted_timestamps = [pd.to_datetime(ts).strftime('%H:%M:%S') for ts in timestamps]
    return formatted_timestamps

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
    print(f"An error occurred: {e}")





