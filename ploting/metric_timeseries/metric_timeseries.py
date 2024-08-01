import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import MonthLocator, YearLocator, DateFormatter
from datetime import datetime

# Choose device
device = 'sh1'
#device = 'sh2'

# Directory containing the CSV files
directory = f'/mnt/4tbssd/daily_metrics/{device}'

# Define the date range
start_date = '2018-01-01'
end_date = '2024-07-10'

# Choose metric
#metric = 'Min (dBm)'
#metric = 'Max (dBm)'
#metric = 'Skew'
metric = 'Kurtosis'
#metric = 'Mean (dBm)'
#metric = 'Median (dBm)'

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

# Calculate the daily average of the metric across all frequencies
daily_average = all_data.groupby('Date')[metric].mean()

# Plot the daily average metric as a time series
plt.figure(figsize=(14, 6))
plt.plot(daily_average.index, daily_average.values, linestyle='-', color='b')

# Set major ticks to years and minor ticks to months
year_locator = YearLocator()
month_locator = MonthLocator()

plt.gca().xaxis.set_major_locator(year_locator)
plt.gca().xaxis.set_minor_locator(month_locator)

# Format the major ticks to show years
plt.gca().xaxis.set_major_formatter(DateFormatter('%Y'))

# Disable minor tick labels
plt.gca().xaxis.set_minor_formatter(plt.NullFormatter())

# Add grid lines for each month
plt.grid(True, which='major', axis='x', linestyle='-', alpha=0.7)  # Major grid lines for years
plt.grid(True, which='minor', axis='x', linestyle='--', alpha=0.5)  # Minor grid lines for months

plt.title(f'Daily Average {metric} for {device.upper()} from {start_date} to {end_date}')
plt.xlabel('Date')
plt.ylabel(f'Average {metric}')
plt.tight_layout()
plt.show()
