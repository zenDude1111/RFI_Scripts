import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Define the paths
input_csv_path = '/mnt/4tbssd/time_series_matrix_data/sh1/2024/20240516_matrix.csv'
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

# Determine the range of your data for contour levels
#min_power = np.min(power_readings)
#max_power = np.max(power_readings)
levels = np.linspace(-110,-20, 25)  # Adjust number of levels as needed

# Create the contour plot
plt.figure(figsize=(20, 12))
c = plt.contourf(F, T, power_readings, levels=levels, cmap='cividis')

# Labeling
plt.xlabel('Frequency (GHz)')
plt.ylabel('Time since midnight (hours)')
plt.title('20240516 SH1-MAPO')
plt.colorbar(c, label='Power (dBm)')

# Save and optionally display the plot
plt.tight_layout()
# Save the plot with high resolution
plt.savefig(output_plot_path, dpi=100)
#plt.show()
