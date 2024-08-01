import os
import pandas as pd
import numpy as np
from datetime import datetime
from scipy.stats import ttest_ind

# Choose device
device = 'sh2'

# Directory containing the CSV files
directory = f'/mnt/4tbssd/daily_metrics/{device}'

# Define the date range
start_date = '2018-01-01'
end_date = '2024-07-10'

# Choose metric
#metric = 'Kurtosis'
metric = 'Skew'

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

# Extract the month from the Date for seasonal separation
all_data['Month'] = all_data['Date'].dt.month

# Define Austral summer and winter months
summer_months = [10, 11, 12, 1, 2, 3]
winter_months = [4, 5, 6, 7, 8, 9]

# Prepare a list to store results
results = []

# Group by Frequency and calculate statistics for each frequency bin
for frequency, group in all_data.groupby('Frequency (GHz)'):
    # Filter data for each season
    summer_data = group[group['Month'].isin(summer_months)][metric]
    winter_data = group[group['Month'].isin(winter_months)][metric]
    
    # Calculate summary statistics
    summer_mean = summer_data.mean()
    winter_mean = winter_data.mean()
    summer_std = summer_data.std()
    winter_std = winter_data.std()
    
    # Perform Welch's t-test (assuming unequal variances)
    t_stat, p_value = ttest_ind(summer_data, winter_data, equal_var=False)
    
    # Store the results
    results.append({
        'Frequency (GHz)': frequency,
        'Summer Mean': summer_mean,
        'Summer Std': summer_std,
        'Winter Mean': winter_mean,
        'Winter Std': winter_std,
        'T-statistic': t_stat,
        'P-value': p_value
    })

# Convert results to a DataFrame
results_df = pd.DataFrame(results)

# Specify the output directory
output_directory = '/home/polarbear/Desktop/erics_code/seasonal_metrics/csvs'

# Ensure the directory exists
os.makedirs(output_directory, exist_ok=True)

# Specify the output file path
output_file = os.path.join(output_directory, f'seasonal_stats_{device}_{metric}.csv')

# Save the results to the specified file path
results_df.to_csv(output_file, index=False)
print(f"Results saved to {output_file}")
