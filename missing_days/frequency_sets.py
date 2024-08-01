import os
import pandas as pd
from datetime import datetime

# Directory containing the CSV files
directory = '/mnt/4tbssd/daily_metrics/sh2'

# Define the date range
start_date = '2018-01-01'
end_date = '2024-07-10'

# Convert the date range to datetime objects
start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')

# Prepare a list to store the data
all_data = []

# Process each file in the directory
for filename in os.listdir(directory):
    if filename.endswith('_metrics.csv'):
        # Extract the date from the filename and convert it to a datetime object
        file_date_str = filename.split('_')[0]
        file_date_dt = datetime.strptime(file_date_str, '%Y%m%d')
        
        # Check if the file date is within the specified range
        if start_date_dt <= file_date_dt <= end_date_dt:
            # Read the CSV file
            file_path = os.path.join(directory, filename)
            data = pd.read_csv(file_path)
            
            # Add the date to the data
            data['Date'] = file_date_dt
            
            # Append the data to the all_data list
            all_data.append(data[['Frequency (GHz)', 'Date']])

# Concatenate all dataframes in the list into a single DataFrame
all_data = pd.concat(all_data, ignore_index=True)

# Group by date and aggregate the frequencies into sets
frequency_sets = all_data.groupby('Date')['Frequency (GHz)'].apply(lambda x: frozenset(x)).reset_index()
frequency_sets.columns = ['Date', 'Frequency Set']

# Get unique frequency sets
unique_frequency_sets = frequency_sets['Frequency Set'].unique()

# Create a mapping of frequency sets to a unique identifier
frequency_set_mapping = {fs: idx for idx, fs in enumerate(unique_frequency_sets)}

# Map each date to its corresponding frequency set identifier
frequency_sets['Frequency Set ID'] = frequency_sets['Frequency Set'].map(frequency_set_mapping)

# Save the sorted days with their frequency set identifiers to a CSV file
frequency_sets.to_csv('sorted_days_with_frequency_sets.csv', index=False)

print(f"Found {len(unique_frequency_sets)} unique frequency sets.")
print("Days sorted into their frequency sets have been saved to 'sorted_days_with_frequency_sets.csv'.")
