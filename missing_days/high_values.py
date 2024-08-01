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
            all_data.append(data[['Frequency (GHz)', 'Max (dBm)', 'Date']])

# Concatenate all dataframes in the list into a single DataFrame
all_data = pd.concat(all_data, ignore_index=True)

# Filter the data to find frequencies and days with dBm value higher than -10
filtered_data = all_data[all_data['Max (dBm)'] > -10]

# Save the filtered data to a CSV file
filtered_data.to_csv('high_dbm_values.csv', index=False)

print("Frequencies and days with dBm value higher than -10 have been saved to 'high_dbm_values.csv'.")
