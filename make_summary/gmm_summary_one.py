import pandas as pd
import numpy as np
import os
from sklearn.mixture import GaussianMixture

# Define base directory paths
input_file_path = '/mnt/4tbssd/time_series_matrix_data/sh1/2021/20210101_matrix.csv'  # Update with the specific file path
output_base_path = '/mnt/4tbssd/gmm_reports/sh1/'

# Ensure the output base path exists
os.makedirs(output_base_path, exist_ok=True)

# Specific frequency channel to focus on
target_frequency = 8.0995  # Example frequency in GHz, adjust as needed

def fit_gmm(n_components, data):
    gmm = GaussianMixture(n_components=n_components)
    gmm.fit(data)
    bic = gmm.bic(data)
    return (bic, gmm)

def process_file(file_path, target_frequency):
    df = pd.read_csv(file_path)
    target_data = df[df['Frequency (GHz)'] == target_frequency].drop(columns=['Frequency (GHz)'])

    if target_data.empty:
        raise ValueError(f"No data found for frequency {target_frequency} GHz in file {file_path}")

    # Automatically determine the number of components
    lowest_bic = np.inf
    best_gmm = None

    for n_components in range(1, 4):  # Adjust range as needed
        bic, gmm = fit_gmm(n_components, target_data.T)
        if bic < lowest_bic:
            lowest_bic = bic
            best_gmm = gmm

    # Use the best GMM found
    num_components = best_gmm.n_components
    means = best_gmm.means_.flatten()

    # Pad means with zeros to ensure the length is consistent
    max_components = 5  # Maximum number of components to consider
    padded_means = np.zeros(max_components)
    padded_means[:len(means)] = means

    # Extracting date from the file path
    date_part = os.path.basename(file_path).split('_')[0]

    # Create a DataFrame for the results
    result_data = {
        'Date': [date_part],
        'Num Components': [num_components],
    }
    for i in range(max_components):
        result_data[f'Mean Component {i + 1} (dBm)'] = [padded_means[i]]

    result_df = pd.DataFrame(result_data)
    return result_df

try:
    # Process the single file
    summary_df = process_file(input_file_path, target_frequency)

    # Save the final summary file
    output_summary_path = os.path.join(output_base_path, f'{target_frequency}_GHz_gmm_summary.csv')
    summary_df.to_csv(output_summary_path, index=False)
    print(f'Summary statistics written to {output_summary_path}')
except Exception as e:
    print(f"Error processing file {input_file_path}: {e}")


