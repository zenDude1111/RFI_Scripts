import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def plot_waterfall(date: str):

    # Signal Hound 1 paths
    #input_csv_path = f'/mnt/4tbssd/time_series_matrix_data/sh1/2024/{date}_matrix.csv'
    #output_plot_path = f'/mnt/4tbssd/waterfall_plots/sh1/sh1_{date}.png'

    # Signal Hound 2 paths
    input_csv_path = f'/mnt/4tbssd/time_series_matrix_data/sh2/2024/{date}_matrix.csv'
    output_plot_path = f'/mnt/4tbssd/waterfall_plots/sh2/sh2_{date}.png'

    # Anritsu paths
    #input_csv_path = f'/mnt/4tbssd/time_series_matrix_data/anritsu/2024/{date}_matrix.csv'
    #output_plot_path = f'/mnt/4tbssd/waterfall_plots/anritsu/anritsu_{date}.png'
    
    # Read the CSV file
    data = pd.read_csv(input_csv_path, index_col='Frequency (GHz)')

    # Function to convert timestamps to hours since midnight
    def hours_since_midnight(s):
        dt = pd.to_datetime(s)
        return dt.hour + dt.minute / 60 + dt.second / 3600

    # Convert the column headers (timestamps) to hours since midnight
    time_stamps = [hours_since_midnight(ts) for ts in data.columns]

    # Ensure timestamps are sorted
    sorted_indices = np.argsort(time_stamps)
    sorted_time_stamps = np.array(time_stamps)[sorted_indices]
    sorted_data = data.iloc[:, sorted_indices]

    # Aggregate every 16 frequency channels by taking the max value
    aggregated_data = sorted_data.groupby(np.arange(len(sorted_data)) // 4).max()

    # Update the frequency index to reflect the aggregated intervals
    freq_index = np.linspace(data.index.min(), data.index.max(), len(aggregated_data))
    aggregated_data.index = freq_index

    # Create a continuous time axis
    min_time = np.floor(min(sorted_time_stamps))
    max_time = np.ceil(max(sorted_time_stamps))
    continuous_time_stamps = np.linspace(min_time, max_time, len(sorted_time_stamps))

    # Interpolate data to fit the continuous time axis
    interpolated_data = pd.DataFrame(index=aggregated_data.index, columns=continuous_time_stamps)
    for freq in aggregated_data.index:
        interpolated_data.loc[freq] = np.interp(continuous_time_stamps, sorted_time_stamps, aggregated_data.loc[freq])

    # Ensure all values are finite
    interpolated_data = interpolated_data.replace([np.inf, -np.inf], np.nan).ffill().bfill()

    # Create meshgrid for frequencies and times
    F, T = np.meshgrid(interpolated_data.index, continuous_time_stamps)

    # Transpose the data to align with the meshgrid
    power_readings = interpolated_data.values.T

    # Set the range based on pre-determined values
    levels = np.linspace(-110, -20, 25)  # Signal Hound range

    # Create the contour plot
    plt.figure(figsize=(18, 7), constrained_layout=True)
    
    c = plt.contourf(F, T, power_readings, levels=levels, cmap='viridis')

    # Labeling
    plt.xlabel('Frequency (GHz)')
    plt.ylabel('Time since midnight (hours)')
    #plt.title(f'{date} SH1-MAPO') # SH1 title
    plt.title(f'{date} SH2-DSL Aggregate 4') # SH2 title
    #plt.title(f'{date} Anritsu-DSL') # Anritsu title
    plt.colorbar(c, label='Power (dBm)')

    # Set x-axis ticks to every 2 GHz (adjust as needed)
    min_freq = interpolated_data.index.min()
    max_freq = interpolated_data.index.max()
    freq_ticks = np.arange(min_freq, max_freq, 0.5)  # Adjust the step size to control the number of ticks
    plt.xticks(freq_ticks)

    # Set y-axis ticks starting from the minimum time value to the maximum, in 2-hour intervals
    time_ticks = np.arange(min_time, max_time, 2)
    plt.yticks(time_ticks)

    # Save or show the plot
    #plt.savefig(output_plot_path)
    plt.show()
    plt.close()

# Loop through days and plot waterfalls
#for i in range(20240701, 20240732):
    #date = str(i)
    #plot_waterfall(date)

plot_waterfall('20240502')

