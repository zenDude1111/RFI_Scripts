import pandas as pd
import matplotlib.pyplot as plt 
import numpy as np

def plot_waterfall(date: str):

    input_csv_path = f'/mnt/4tbssd/time_series_matrix_data/sh1/2024/{date}_matrix.csv'

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

    #make all power readings -110
    power_readings = np.full_like(power_readings, -110)

    # Set the range based on pre-determined values
    levels = np.linspace(-110, -20, 25)  # Signal Hound range

    # Create the contour plot
    plt.figure(figsize=(18, 7), constrained_layout=True)
    
    c = plt.contourf(F, T, power_readings, levels=levels, cmap='viridis')

    # Labeling
    plt.xlabel('Frequency (GHz)', )
    plt.ylabel('Time since midnight (hours)')
    plt.title(f'No Data Available') #SH1 title
    plt.colorbar(c, label='Power (dBm)')

    # Set x-axis ticks to every half GHz
    min_freq = data.index.min()
    max_freq = data.index.max()
    freq_ticks = np.arange(min_freq, max_freq, 0.5)
    plt.xticks(freq_ticks)

    # Set y-axis ticks starting from the minimum time value to the maximum, in 3-hour intervals
    min_time = np.floor(min(time_stamps))
    max_time = np.ceil(max(time_stamps))
    time_ticks = np.arange(min_time, max_time, 2)
    plt.yticks(time_ticks)

    # Add "No data available" text in the middle of the plot
    plt.text(6.2, 12, 'No data available', horizontalalignment='center', 
             verticalalignment='center', fontsize=20, color='red')

    #plt.show()
    plt.savefig(f'/mnt/4tbssd/waterfall_plots/blank_waterfall.png')
    plt.close()

plot_waterfall('20240501')
