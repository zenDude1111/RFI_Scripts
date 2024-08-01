import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Path for SignalHound 1
input_csv_path = '/mnt/4tbssd/time_series_matrix_data/sh1/2021/20210101_matrix.csv'

# Read the CSV file
data = pd.read_csv(input_csv_path, index_col='Frequency (GHz)')

# Function to convert timestamps to hours since midnight
def hours_since_midnight(s):
    dt = pd.to_datetime(s)
    return dt.hour + dt.minute / 60 + dt.second / 3600

# Convert the column headers (timestamps) to hours since midnight
time_stamps = [hours_since_midnight(ts) for ts in data.columns]

# Create meshgrid for frequencies and times
F, T = np.meshgrid(data.index, time_stamps)

# Transpose the data to align with the meshgrid
power_readings_dBm = data.values.T

# Convert dBm to mW
power_readings_mW = 10 ** (power_readings_dBm / 10)

# Calculate the median for each frequency channel in mW
medians_mW = np.median(power_readings_mW, axis=0)

# Subtract the median in mW
median_subtracted_power_mW = power_readings_mW - medians_mW

# To avoid log(0) issues, set any negative or zero values to a very small positive number
median_subtracted_power_mW[median_subtracted_power_mW <= 0] = 1e-12

# Convert back to dBm
median_subtracted_power_dBm = 10 * np.log10(median_subtracted_power_mW)

# Apply filtering to the power readings
filtered_power_readings = np.where(median_subtracted_power_dBm < -110, -110, median_subtracted_power_dBm)

# Set appropriate levels for dBm deviations
levels = np.linspace(-110, -20, 25)  

# Create the contour plot
plt.figure(figsize=(20, 12))
c = plt.contourf(F, T, filtered_power_readings, levels=levels, cmap='cividis')

# Labeling
plt.xlabel('Frequency (GHz)')
plt.ylabel('Time since midnight (hours)')
plt.title('Median Subtracted 20210101 SH1-MAPO')
plt.colorbar(c, label='Power (dBm)')

# Display the plot
plt.tight_layout()
plt.show()
