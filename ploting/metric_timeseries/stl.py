import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from statsmodels.tsa.seasonal import STL

# Choose device and metric
device = 'sh2'
metric = 'Skew'  # Replace with the desired metric, e.g., 'Min (dBm)', 'Max (dBm)', etc.

# Directory containing the CSV files
directory = f'/mnt/4tbssd/daily_metrics/{device}'

# Define the date range
start_date = '2018-01-01'
end_date = '2024-03-01'

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
            all_data.append(data[['Date', metric]])

# Concatenate all dataframes in the list into a single DataFrame
all_data = pd.concat(all_data, ignore_index=True)

# Handle duplicate dates by grouping and taking the mean
all_data = all_data.groupby('Date').mean()

# Ensure the data is sorted by date
all_data.sort_index(inplace=True)

# Ensure the data is in a time series format with a regular frequency
all_data = all_data.asfreq('D')

# Fill missing values if any (optional)
all_data[metric] = all_data[metric].ffill()

# Perform STL decomposition
stl = STL(all_data[metric], seasonal=365)  # Adjust `seasonal` as needed
result = stl.fit()

# Plot the STL decomposition results with smaller plots
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8))
result.trend.plot(ax=ax1)
ax1.set_ylabel('Trend')
ax1.set_title('STL Decomposition - Trend Component')

result.seasonal.plot(ax=ax2)
ax2.set_ylabel('Seasonal')
ax2.set_title('STL Decomposition - Seasonal Component')

result.resid.plot(ax=ax3)
ax3.set_ylabel('Residual')
ax3.set_title('STL Decomposition - Residual Component')

# Adjust layout to ensure the title is not cut off
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.suptitle(f'STL Decomposition of {metric} - {device.upper()}\n(2018-2024)', fontsize=16, y=1.02)
plt.subplots_adjust(top=0.85)  # Increase the top margin

plt.show()
