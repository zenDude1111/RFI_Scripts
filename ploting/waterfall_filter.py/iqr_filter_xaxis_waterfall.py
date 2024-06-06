import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Path for Anritsu
#input_csv_path = '/mnt/4tbssd/time_series_matrix_data/anritsu/2024/20240501_matrix.csv'
# output_plot_path = '/mnt/4tbssd/waterfall_plots/anritsu/anritsu_20240516.png'

# Path for SignalHound 1
# input_csv_path = '/mnt/4tbssd/time_series_matrix_data/sh1/2024/20240501_matrix.csv'
# output_plot_path = '/mnt/4tbssd/waterfall_plots/sh1/sh1_20240516.png'

# Path for SignalHound 2
input_csv_path = '/mnt/4tbssd/time_series_matrix_data/sh2/2024/20240501_matrix.csv'
# output_plot_path = '/mnt/4tbssd/waterfall_plots/sh1/sh1_20240516.png'

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
power_readings = data.values.T

# Calculate the IQR for each time (each row)
Q1 = np.percentile(power_readings, 25, axis=1)
Q3 = np.percentile(power_readings, 75, axis=1)
IQR = Q3 - Q1

# Reshape Q1, Q3, and IQR to match the shape of power_readings for broadcasting
Q1 = Q1[:, np.newaxis]
Q3 = Q3[:, np.newaxis]
IQR = IQR[:, np.newaxis]

# Define the cutoff as Q3 + 1.5 * IQR
cutoff = Q3 + 1.5 * IQR

# Anritsu thresholding to set values below the cutoff to -90 dBm
#filtered_power_readings = np.where(power_readings < cutoff, -90, power_readings)

# Signal Hound thresholding to set values below the cutoff to -110 dBm
filtered_power_readings = np.where(power_readings < cutoff, -110, power_readings)

# Range for Anritsu
#levels = np.linspace(-90, -20, 25)

# Range for Signal Hounds
levels = np.linspace(-110, -20, 25)

# Create the contour plot
plt.figure(figsize=(20, 12))
c = plt.contourf(F, T, filtered_power_readings, levels=levels, cmap='cividis')

# Labeling
plt.xlabel('Frequency (GHz)')
plt.ylabel('Time since midnight (hours)')
plt.title('IQR Filter 20240501 Anritsu-DSL')  # Anritsu title
# plt.title('IQR Filter 20240501 SH1-MAPO')  # SH1 title
# plt.title('IQR Filter 20240501 SH2-DSL')  # SH2 title
plt.colorbar(c, label='Power (dBm)')

# Save and optionally display the plot
plt.tight_layout()
# plt.savefig(output_plot_path, dpi=100)
plt.show()
