import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Define the paths
input_csv_path = '/mnt/4tbssd/anritsu/anritsu/20240516_matrix.csv'
output_plot_path = '/mnt/4tbssd/plots/anritsu_20240516.png'

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
levels = np.linspace(-110, -20, 25)  # Adjust number of levels as needed

# Create the contour plot
plt.figure(figsize=(10, 6))  # figsize in inches, (10 inches x 100 dpi = 1000 pixels, 6 inches x 100 dpi = 600 pixels)
c = plt.contourf(F, T, power_readings, levels=levels, cmap='cividis')

# Labeling
plt.xlabel('Frequency (GHz)')
plt.ylabel('Time since midnight (hours)')
plt.title('20240516_anritsu')
plt.colorbar(c, label='Power (dBm)')

# Save and optionally display the plot
plt.tight_layout()
# Save the plot with high resolution
plt.savefig(output_plot_path, dpi=100)  # dpi is set to 100 to get the desired resolution
# plt.show()
