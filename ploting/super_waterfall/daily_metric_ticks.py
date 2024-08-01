import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Choose device
#device = 'sh1'
device = 'sh2'

# Directory containing the CSV files
directory = f'/mnt/4tbssd/daily_metrics/{device}'

# Define the date range
start_date = '2018-01-01'
end_date = '2024-07-10'

# Choose metric
#metric = 'Min (dBm)'
#metric = 'Max (dBm)'
metric = 'Skew'
#metric = 'Kurtosis'

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

# Create a complete date range
complete_date_range = pd.date_range(start=start_date_dt, end=end_date_dt, freq='D')

# Pivot the data to have dates as rows and frequencies as columns
pivot_data = all_data.pivot(index='Date', columns='Frequency (GHz)', values=metric)

# Reindex the pivot table to include all dates, filling missing dates with NaN
pivot_data = pivot_data.reindex(complete_date_range)

# Create a meshgrid for plotting
X, Y = np.meshgrid(pivot_data.columns, pivot_data.index)

# Create the contour plot
plt.figure(figsize=(14, 10))
cp = plt.contourf(X, Y, pivot_data.values, cmap='viridis', levels=np.linspace(pivot_data.min().min(), pivot_data.max().max(), 100))
#cp = plt.contourf(X, Y, pivot_data.values, cmap='viridis', levels=np.linspace(pivot_data.min().min(), 7, 100))
plt.colorbar(cp)
if device == 'sh1':
    plt.title(f'20170101-20240710 SH1-MAPO Daily {metric}')
elif device == 'sh2':
    plt.title(f'20170101-20240710 SH2-DSL Daily {metric}')
plt.xlabel('Frequency (GHz)')
plt.ylabel('Date')

# Set frequency ticks every half GHz
frequency_ticks = np.arange(pivot_data.columns.min(), pivot_data.columns.max() + 0.5, 0.5)
plt.xticks(ticks=frequency_ticks)

# Set date ticks every month
date_ticks = pd.date_range(start=start_date_dt, end=end_date_dt, freq='M')
plt.yticks(ticks=date_ticks, labels=date_ticks.strftime('%Y-%m'))

plt.tight_layout()

# Show missing days in white
plt.contourf(X, Y, np.isnan(pivot_data.values), levels=[0.5, 1.5], colors=['white'])

plt.show()
