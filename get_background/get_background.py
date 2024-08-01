import pandas as pd
import os
import glob

# Path to the directory containing the CSV files
directory_path = '/mnt/4tbssd/day_reports/anritsu/'

# Initialize an empty DataFrame to store the aggregated data
aggregated_data = pd.DataFrame()

# Read all CSV files in the directory
for file_path in glob.glob(os.path.join(directory_path, '*.csv')):
    # Read the CSV file
    data = pd.read_csv(file_path)
    
    # Calculate the power value 5 sigma away from the median
    data['5_Sigma_Away'] = data['Median (dBm)'] + 5 * (data['Max (dBm)'] - data['Min (dBm)']) / 6
    
    # Append to the aggregated DataFrame
    aggregated_data = pd.concat([aggregated_data, data], ignore_index=True)

# Group by Frequency and calculate the average Median and average 5_Sigma_Away
result = aggregated_data.groupby('Frequency (GHz)').agg(
    Avg_Median=('Median (dBm)', 'mean'),
    Avg_5_Sigma_Away=('5_Sigma_Away', 'mean')
).reset_index()

# Save the result to a new CSV file
output_file_path = '/home/polarbear/Desktop/erics_code/anritsu_background/average_median_5_sigma_results.csv'
result.to_csv(output_file_path, index=False)


# Display the result
result.head()


