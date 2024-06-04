import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Define the paths
input_csv_path = '/mnt/4tbssd/time_series_matrix_data/sh1/2021/20210101_matrix.csv'
output_plot_path = '/mnt/4tbssd/plots/large_20210101.png'

# Read the CSV file
data = pd.read_csv(input_csv_path, index_col='Frequency (GHz)')

# Filter the data to start at 1 GHz and sample every 140 channels
filtered_data = data.loc[1:].iloc[::1]

# Function to convert timestamps to hours since midnight
def hours_since_midnight(s):
    return (pd.to_datetime(s).hour + pd.to_datetime(s).minute / 60 + pd.to_datetime(s).second / 3600)

# Convert the column headers (timestamps) to hours since midnight
time_stamps = [hours_since_midnight(ts) for ts in filtered_data.columns]

# Create meshgrid for frequencies and times
F, T = np.meshgrid(filtered_data.index, time_stamps)

# Transpose the data to align with the meshgrid
power_readings = filtered_data.values.T

# Sample every 7th power reading
sampled_power_readings = power_readings[:, ::1]

# Determine the range of your data for contour levels
levels = np.linspace(-110, -20, 25)  # Adjust number of levels as needed

# Create the contour plot
plt.figure(figsize=(20, 12))
c = plt.contourf(F[:, ::1], T[:, ::1], sampled_power_readings, levels=levels, cmap='cividis')

# Labeling
plt.xlabel('Frequency (GHz)')
plt.ylabel('Time since midnight (hours)')
plt.title('20240516_anritsu')
plt.colorbar(c, label='Power (dBm)')

# Save and optionally display the plot
plt.tight_layout()
# Save the plot with high resolution
#plt.savefig(output_plot_path, dpi=100)
plt.show()

