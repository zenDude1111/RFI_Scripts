import os
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.mixture import GaussianMixture
import matplotlib.pyplot as plt

# Choose device
device = 'sh2'

# Directory containing the CSV files
directory = f'/mnt/4tbssd/daily_metrics/{device}'

# Define the date range
start_date = '2018-01-01'
end_date = '2024-07-10'

# Choose metric
metric = 'Skew'

# Convert the date range to datetime objects
start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')

# Prepare a list to store the data
all_data = []

# Process each file in the directory
for filename in os.listdir(directory):
    if filename.endswith('_metrics.csv'):
        # Extract the date from the filename and convert it to a datetime object
        file_date_str = filename.split('_')[0]
        file_date_dt = datetime.strptime(file_date_str, '%Y%m%d')
        
        # Check if the file date is within the specified range
        if start_date_dt <= file_date_dt <= end_date_dt:
            # Read the CSV file
            file_path = os.path.join(directory, filename)
            data = pd.read_csv(file_path)
            
            # Add the date to the data
            data['Date'] = file_date_dt
            
            # Append the data to the all_data list
            all_data.append(data[['Frequency (GHz)', metric, 'Date']])

# Concatenate all dataframes in the list into a single DataFrame
all_data = pd.concat(all_data, ignore_index=True)

# Pivot the data to have dates as rows and frequencies as columns
pivot_data = all_data.pivot(index='Date', columns='Frequency (GHz)', values=metric)

# Reindex the pivot table to include all dates, filling missing dates with NaN
pivot_data = pivot_data.reindex(pd.date_range(start=start_date_dt, end=end_date_dt, freq='D'))

# Handling missing data: filling NaN values with the column mean
pivot_data.fillna(pivot_data.mean(axis=0), inplace=True)

# Transpose the data to have frequencies as rows and dates as columns
data_for_gmm = pivot_data.T

# Fit the GMM
n_components = 3  # Change this number based on the desired number of clusters
gmm = GaussianMixture(n_components=n_components, random_state=0)
gmm.fit(data_for_gmm)

# Predict cluster labels for each frequency
labels = gmm.predict(data_for_gmm)

# Add the cluster labels to the data
data_for_gmm['Cluster'] = labels

# Visualize the results
plt.figure(figsize=(12, 8))
for cluster in range(n_components):
    # Extract data for the current cluster
    cluster_data = data_for_gmm[data_for_gmm['Cluster'] == cluster].drop('Cluster', axis=1).T
    plt.plot(cluster_data.index, cluster_data, label=f'Cluster {cluster + 1}')

plt.title(f'Clustered Frequencies Based on {metric} Seasonal Variations ({device})')
plt.xlabel('Date')
plt.ylabel(f'{metric} Value')
plt.legend()
plt.tight_layout()
plt.show()
