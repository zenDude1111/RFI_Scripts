import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.mixture import GaussianMixture

# Path for Anritsu
#input_csv_path = '/mnt/4tbssd/time_series_matrix_data/anritsu/2024/20240601_matrix.csv'
#output_plot_path = '/mnt/4tbssd/waterfall_plots/anritsu/anritsu_20240516.png'

# Path for SignalHound 1
input_csv_path = '/mnt/4tbssd/time_series_matrix_data/sh1/2021/20210101_matrix.csv'
#output_plot_path = '/mnt/4tbssd/waterfall_plots/sh1/sh1_20240516.png'

# Path for SignalHound 2
#input_csv_path = '/mnt/4tbssd/time_series_matrix_data/sh2/2024/20240601_matrix.csv'
#output_plot_path = '/mnt/4tbssd/waterfall_plots/sh1/sh1_20240516.png'

# Lab SH paths
#input_csv_path = f"/home/polarbear/Desktop/erics_code/lab_sh_data/20240611_matrix.csv"
#output_plot_path = f"/home/polarbear/Desktop/erics_code/lab_sh_data"  # Specify your output directory here

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

# Initialize the filtered power readings array
filtered_power_readings = np.zeros_like(power_readings)

# Apply GMM for each frequency channel
for i in range(power_readings.shape[1]):
    channel_data = power_readings[:, i].reshape(-1, 1)
    gmm = GaussianMixture(n_components=2, random_state=0).fit(channel_data)
    labels = gmm.predict(channel_data)
    component_means = gmm.means_.flatten()
    lowest_component = np.argmin(component_means)
    filtered_power_readings[:, i] = np.where(labels == lowest_component, np.min(channel_data), channel_data.flatten())

# Range for Anritsu
#levels = np.linspace(-90, -20, 25)

# Range for Signal Hounds
levels = np.linspace(-110, -20, 25)

# Create the contour plot
plt.figure(figsize=(20, 12))
c = plt.contourf(F, T, filtered_power_readings, levels=levels, cmap='cividis')  # for filtered power readings
#c = plt.contourf(F, T, power_readings, levels=levels, cmap='cividis')  # for unfiltered power readings

# Labeling
plt.xlabel('Frequency (GHz)')
plt.ylabel('Time since midnight (hours)')
#plt.title('IQR Filter 20240601 Anritsu-DSL')  # Anritsu title
plt.title('GMM Filtered 20210101 SH1-MAPO')  # SH1 title
#plt.title('IQR Filter 20240601 SH2-DSL')  # SH2 title
plt.colorbar(c, label='Power (dBm)')

# Save and optionally display the plot
plt.tight_layout()
#plt.savefig(output_plot_path, dpi=100)
plt.show()
