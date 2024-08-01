import os
import pandas as pd
import numpy as np

# Define the directory containing the CSV files
directory = "/mnt/4tbssd/daily_metrics/sh1"  # Update this path to where your files are located

# Initialize a list to hold the data from all files
data_list = []

# Loop through all files in the directory
for filename in os.listdir(directory):
    if filename.endswith("_metrics.csv"):
        file_path = os.path.join(directory, filename)
        # Read only the necessary columns from the CSV file
        df = pd.read_csv(file_path, usecols=["Frequency (GHz)", "Max (dBm)"])
        # Extract the date from the filename
        date_str = filename.split("_")[0]
        df["Date"] = pd.to_datetime(date_str, format='%Y%m%d')
        # Append the dataframe to the list
        data_list.append(df)

# Concatenate all the dataframes into a single dataframe
all_data = pd.concat(data_list, ignore_index=True)

# Ensure all frequencies are present for each date
all_frequencies = all_data["Frequency (GHz)"].unique()

# Generate a date range covering the entire period of interest
date_range = pd.date_range(start=all_data["Date"].min(), end=all_data["Date"].max())

# Create a MultiIndex with all dates and all frequencies
multi_index = pd.MultiIndex.from_product([date_range, all_frequencies], names=["Date", "Frequency (GHz)"])

# Reindex the DataFrame to include all combinations of dates and frequencies
all_data.set_index(["Date", "Frequency (GHz)"], inplace=True)
all_data = all_data.reindex(multi_index).reset_index()

# Pivot the dataframe to have Dates as rows and Frequencies as columns
pivot_df = all_data.pivot(index="Date", columns="Frequency (GHz)", values="Max (dBm)")

# Set a threshold for minimum number of non-NaN values required for each row to be considered valid
threshold = len(all_frequencies) * 0.5  # Adjust the threshold as necessary

# Fill entire rows with NaN if they have fewer than the threshold of non-NaN values
pivot_df.loc[pivot_df.count(axis=1) < threshold, :] = np.nan

# Save the pivot dataframe to a CSV file
output_csv_path = "/home/polarbear/Desktop/erics_code/RFI_Scripts/ploting/super_waterfall/sh1_max_matrix.csv"  # Update this path to where you want to save the file
pivot_df.to_csv(output_csv_path)

print(f"Data matrix saved to {output_csv_path}")
