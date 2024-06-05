import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def plot_waterfall(date: str):

    # Signal Hound 1 paths
    #input_csv_path = f'/mnt/4tbssd/time_series_matrix_data/sh1/2024/{date}_matrix.csv'
    #output_plot_path = f'/mnt/4tbssd/waterfall_plots/compare_plots/sh1/sh1_{date}.png'
    
    # Signal Hound 2 paths
    #input_csv_path = f'/mnt/4tbssd/time_series_matrix_data/sh2/2024/{date}_matrix.csv'
    #output_plot_path = f'/mnt/4tbssd/waterfall_plots/compare_plots/sh2/sh2_{date}.png'

    # Anritsu paths
    input_csv_path = f'/mnt/4tbssd/time_series_matrix_data/anritsu/2024/{date}_matrix.csv'
    output_plot_path = f'/mnt/4tbssd/waterfall_plots/compare_plots/anritsu/anritsu_{date}.png'

    # Read the CSV file
    data = pd.read_csv(input_csv_path, index_col='Frequency (GHz)')

    # Filter out frequencies between 1 GHz and 12.4 GHz
    data_filtered = data[(data.index > 1.0) & (data.index <= 12.4)]

    # Function to convert timestamps to hours since midnight
    def hours_since_midnight(s):
        dt = pd.to_datetime(s)
        return dt.hour + dt.minute / 60 + dt.second / 3600

    # Convert the column headers (timestamps) to hours since midnight
    time_stamps = [hours_since_midnight(ts) for ts in data_filtered.columns]

    # Create meshgrid for frequencies and times
    F, T = np.meshgrid(data_filtered.index, time_stamps)

    # Transpose the data to align with the meshgrid
    power_readings = data_filtered.values.T

    # To find the range based on the min and max values in the data
    min_power = np.min(power_readings)
    max_power = np.max(power_readings)

    # Set the range based on pre-determined values
    levels = np.linspace(min_power, max_power, 25)  # min and max range
    #levels = np.linspace(-110, -20, 25)  # Signal Hound range
    #levels = np.linspace(-90,-20, 25)  # Anristu range

    # Create the contour plot
    plt.figure(figsize=(20, 12))
    c = plt.contourf(F, T, power_readings, levels=levels, cmap='cividis')

    # Labeling
    plt.xlabel('Frequency (GHz)')
    plt.ylabel('Time since midnight (hours)')
    #plt.title(f'{date} SH1-MAPO') #SH1 title
    #plt.title(f'{date} SH2-DSL') #SH2 title
    plt.title(f'{date} Anritsu-DSL') #Anritsu title
    plt.colorbar(c, label='Power (dBm)')

    # Save and optionally display the plot
    plt.tight_layout()
    # Save the plot with high resolution
    plt.savefig(output_plot_path, dpi=100)
    # plt.show()

# Loop through days and plot waterfalls
for i in range(20240601, 20240606):
    date = str(i)
    plot_waterfall(date)