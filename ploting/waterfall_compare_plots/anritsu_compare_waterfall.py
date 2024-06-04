import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Define the paths
input_csv_path = '/mnt/4tbssd/anritsu/anritsu/20240516_matrix.csv'
output_plot_path = '/mnt/4tbssd/plots/anritsu_20240516.png'

# Read the CSV file
data = pd.read_csv(input_csv_path, index_col='Frequency (GHz)')

# Filter out frequencies between 1 GHz and 12.4 GHz
data_filtered = data[(data.index > 1.0) & (data.index <= 12.4)]

# Function to convert timestamps to hours since midnight
def hours_since_midnight(s):
    return (pd.to_datetime(s).hour + pd.to_datetime(s).minute / 60 + pd.to_datetime(s).second / 3600)

# Convert the column headers (timestamps) to hours since midnight
time_stamps = [hours_since_midnight(ts) for ts in data.columns]

# Create meshgrid for frequencies and times
F, T = np.meshgrid(data_filtered.index, time_stamps)

# Transpose the data to align with the meshgrid
power_readings = data_filtered.values.T

# Determine the range of your data for contour levels
vmin = np.min(power_readings)
vmax = np.max(power_readings)

# Create the contour plot
plt.figure(figsize=(20, 12))
c = plt.contourf(F, T, power_readings, levels=25, cmap='cividis', vmin=vmin, vmax=vmax)

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
