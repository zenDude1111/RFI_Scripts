import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Choose device
device = 'sh2'

# Directory containing the CSV files
directory = f'/mnt/4tbssd/daily_metrics/{device}'

# Define the date range
start_date = '2018-01-01'
end_date = '2024-07-10'

# Choose metric
metric = 'Max (dBm)'

# Define the frequency range in GHz
freq_min = 0.0001
freq_max = 3.0

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
            all_data.append(data[['Frequency (GHz)', metric, 'Date']])

# Concatenate all dataframes in the list into a single DataFrame
all_data = pd.concat(all_data, ignore_index=True)

# Filter the data based on the frequency range
filtered_data = all_data[(all_data['Frequency (GHz)'] >= freq_min) & (all_data['Frequency (GHz)'] <= freq_max)]

# Pivot the data to have frequencies as rows and dates as columns
pivot_data = filtered_data.pivot(index='Frequency (GHz)', columns='Date', values=metric)

# Only use the existing dates in the data
pivot_data = pivot_data.dropna(axis=1, how='all')  # Drop columns with all NaN values

# Create a meshgrid for plotting
Y, X = np.meshgrid(pivot_data.index, pivot_data.columns)

# Create the contour plot with 25 levels and a value range from -90 to -20
plt.figure(figsize=(12, 6))
cp = plt.contourf(X, Y, pivot_data.values.T, cmap='viridis', levels=np.linspace(-90, -20, 25))
plt.colorbar(cp)
if device == 'sh1':
    plt.title(f'20180101-20240710 SH1-MAPO Daily {metric}')
elif device == 'sh2':
    plt.title(f'20180101-20240710 SH2-DSL Daily {metric}')
plt.xlabel('Date')
plt.ylabel('Frequency (GHz)')
plt.xticks(rotation=45)
plt.tight_layout()

plt.show()
