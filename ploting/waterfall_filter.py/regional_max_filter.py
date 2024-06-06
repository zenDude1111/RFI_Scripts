import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter
from skimage.morphology import reconstruction
from skimage import img_as_float

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

# Convert to float
power_readings = img_as_float(power_readings)

# Apply Gaussian filter for initial smoothing
#smoothed_matrix = gaussian_filter(power_readings, 1)
smoothed_matrix = power_readings

# Perform morphological reconstruction by dilation
seed = np.copy(smoothed_matrix)
seed[1:-1, 1:-1] = smoothed_matrix.min()
mask = smoothed_matrix
dilated = reconstruction(seed, mask, method='dilation')

# Subtract the dilated image from the original to isolate features
isolated_features = smoothed_matrix - dilated

# Plot the results
fig, (ax0, ax1, ax2) = plt.subplots(nrows=1, ncols=3, figsize=(20, 6), sharex=True, sharey=True)

ax0.imshow(smoothed_matrix, aspect='auto', cmap='viridis')
ax0.set_title('Original Image')
ax0.axis('off')

ax1.imshow(dilated, vmin=smoothed_matrix.min(), vmax=smoothed_matrix.max(), aspect='auto', cmap='viridis')
ax1.set_title('Dilated')
ax1.axis('off')

ax2.imshow(isolated_features, aspect='auto', cmap='viridis')
ax2.set_title('Isolated Features (Image - Dilated)')
ax2.axis('off')

fig.tight_layout()
plt.show()

# Using h-dome technique
h = 0.1
seed = smoothed_matrix - h
dilated_h = reconstruction(seed, mask, method='dilation')
hdome = smoothed_matrix - dilated_h

# Plot the h-dome results
fig, (ax0, ax1, ax2) = plt.subplots(nrows=1, ncols=3, figsize=(20, 6))

ax0.plot(mask[100], '0.5', label='mask')
ax0.plot(seed[100], 'k', label='seed')
ax0.plot(dilated_h[100], 'r', label='dilated')
ax0.set_ylim(-0.2, 2)
ax0.set_title('Image Slice')
ax0.set_xticks([])
ax0.legend()

ax1.imshow(dilated_h, vmin=smoothed_matrix.min(), vmax=smoothed_matrix.max(), aspect='auto', cmap='viridis')
ax1.axhline(100, color='r', alpha=0.4)
ax1.set_title('Dilated')
ax1.axis('off')

ax2.imshow(hdome, aspect='auto', cmap='viridis')
ax2.axhline(100, color='r', alpha=0.4)
ax2.set_title('Image - Dilated (h-dome)')
ax2.axis('off')

fig.tight_layout()
plt.show()
