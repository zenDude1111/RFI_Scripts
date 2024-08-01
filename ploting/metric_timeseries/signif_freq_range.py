import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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
#metric = 'Min (dBm)'
#metric = 'Max (dBm)'
#metric = 'Skew'
metric = 'Kurtosis'
#metric = 'Mean (dBm)'
#metric = 'Median (dBm)'

# Choose band and define band name and frequency range
# VLF (Very Low Frequency)
#freq_min, freq_max = 0.003, 0.03
#band_name = "VLF"

# LF (Low Frequency)
#freq_min, freq_max = 0.03, 0.3
#band_name = "LF"

# MF (Medium Frequency)
#freq_min, freq_max = 0.3, 1
#band_name = "MF"

# L-band
freq_min, freq_max = 1, 2
band_name = "L-band"

# S-band
#freq_min, freq_max = 2, 4
#band_name = "S-band"

# C-band
#freq_min, freq_max = 4, 8
#band_name = "C-band"

# X-band
#freq_min, freq_max = 8, 12.4
#band_name = "X-band"

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

# Extract the month from the Date for seasonal separation
filtered_data['Month'] = filtered_data['Date'].dt.month

# Define Austral summer and winter months
summer_months = [10, 11, 12, 1, 2, 3]
winter_months = [4, 5, 6, 7, 8, 9]

# Filter data for each season
summer_data = filtered_data[filtered_data['Month'].isin(summer_months)][metric]
winter_data = filtered_data[filtered_data['Month'].isin(winter_months)][metric]

# Calculate summary statistics
summer_mean = summer_data.mean()
winter_mean = winter_data.mean()
summer_std = summer_data.std()
winter_std = winter_data.std()

# Perform Welch's t-test (assuming unequal variances)
t_stat, p_value = ttest_ind(summer_data, winter_data, equal_var=False)

# Define a larger number threshold for p-value
threshold = 1e-10

# Check if the p-value is smaller than the threshold
if p_value < threshold:
    p_value_rounded = f"< {threshold:.1e}"
else:
    p_value_rounded = f"{p_value:.10e}"

# Output results of statistical analysis
print(f"Device: {device.upper()}")
print(f"Metric: {metric}")
print(f"Band: {band_name} ({freq_min} - {freq_max} GHz)")
print(f"Austral Summer (Oct-Mar) - Mean: {summer_mean:.4f}, Std: {summer_std:.4f}")
print(f"Austral Winter (Apr-Sep) - Mean: {winter_mean:.4f}, Std: {winter_std:.4f}")
print(f"T-statistic: {t_stat:.4f}, P-value: {p_value_rounded}")
if p_value < 0.05:
    print("The difference between the two seasons is statistically significant.")
else:
    print("The difference between the two seasons is not statistically significant.")

# Visualization of the means and standard deviations
# Labels for the bar plot
seasons = ['Austral Summer (Oct-Mar)', 'Austral Winter (Apr-Sep)']
means = [summer_mean, winter_mean]
errors = [summer_std, winter_std]

# Create the bar plot with reduced height
plt.figure(figsize=(8, 4))
x_pos = np.arange(len(seasons))
bars = plt.bar(x_pos, means, yerr=errors, alpha=0.7, capsize=10, color=['skyblue', 'lightgreen'])

if device == 'sh1':
    device_name = 'SH1-MAPO'
elif device == 'sh2':
    device_name = 'SH2-DSL'
# Add labels and title
plt.xticks(x_pos, seasons, rotation=0, ha='center')
plt.ylabel(f'Mean {metric}')
plt.title(f'{device_name.upper()}: Comparison of Mean {metric} in {band_name} Band ({freq_min}-{freq_max} GHz)\nAustral Summer vs Winter ({start_date} to {end_date})')

# Adjust layout to make room for the additional text
plt.tight_layout(rect=[0, 0.2, 1, 1])  # Leave space at the bottom for text

# Add detailed information under the plot
info_text = (f"Austral Summer (Oct-Mar) - Mean: {summer_mean:.4f}, Std: {summer_std:.4f}\n"
             f"Austral Winter (Apr-Sep) - Mean: {winter_mean:.4f}, Std: {winter_std:.4f}\n"
             f"T-statistic: {t_stat:.4f}, P-value: {p_value_rounded}")
plt.figtext(0.5, 0.05, info_text, ha='center', fontsize=12, wrap=True)

# Display the plot
#plt.show()

# Save directory
save_dir = f'/home/polarbear/Desktop/erics_code/statistical_signif_plots/bands'
if not os.path.exists(save_dir):
    os.makedirs(save_dir)
    
# Save the plot
save_path = os.path.join(save_dir, f'{device}_{band_name}_{metric}.png')
plt.savefig(save_path)

