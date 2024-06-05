import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import medfilt

# Define the paths
input_csv_path = '/mnt/4tbssd/time_series_matrix_data/sh1/2021/20210101_matrix.csv'
output_plot_path = '/mnt/4tbssd/waterfall_plots/sh1/sh1_20240516.png'

# Read the CSV file
data = pd.read_csv(input_csv_path, index_col='Frequency (GHz)')

# Function to convert timestamps to hours since midnight
def hours_since_midnight(s):
    return (pd.to_datetime(s).hour + pd.to_datetime(s).minute / 60 + pd.to_datetime(s).second / 3600)

# Convert the column headers (timestamps) to hours since midnight
time_stamps = [hours_since_midnight(ts) for ts in data.columns]

# Create meshgrid for frequencies and times
F, T = np.meshgrid(data.index, time_stamps)

# Transpose the data to align with the meshgrid
power_readings = data.values.T

# Apply the Wiener filter
filtered_power_readings = medfilt(power_readings)

# Determine the range of your data for contour levels
levels = np.linspace(-90, -20, 25)  # Adjust number of levels as needed

# Create the contour plot
plt.figure(figsize=(20, 12))
c = plt.contourf(F, T, filtered_power_readings, levels=levels, cmap='cividis')

# Labeling
plt.xlabel('Frequency (GHz)')
plt.ylabel('Time since midnight (hours)')
plt.title('20240602 Anritsu-DSL')
plt.colorbar(c, label='Power (dBm)')

# Save and optionally display the plot
plt.tight_layout()
#plt.savefig(output_plot_path, dpi=100)
plt.show()
