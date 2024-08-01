import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn.mixture import GaussianMixture
import numpy as np

def extract_frequency_data(base_folder, start_date, end_date, target_frequency):
    all_data = []
    
    for year_folder in os.listdir(base_folder):
        year_folder_path = os.path.join(base_folder, year_folder)
        
        if os.path.isdir(year_folder_path):
            for csv_file in os.listdir(year_folder_path):
                try:
                    # Extract the date from the file name
                    file_date_str = csv_file.split('_')[0]
                    file_date = datetime.strptime(file_date_str, '%Y%m%d')
                except ValueError:
                    # Skip files that don't match the expected date format
                    continue
                
                # Check if the file is within the specified date range
                if start_date <= file_date <= end_date:
                    file_path = os.path.join(year_folder_path, csv_file)
                    df = pd.read_csv(file_path)
                    
                    # Filter the row with the desired frequency
                    frequency_row = df[df['Frequency (GHz)'] == target_frequency]
                    
                    if not frequency_row.empty:
                        frequency_data = frequency_row.iloc[0, 1:]  # Skip the first column (Frequency)
                        # Combine date and time to form a full timestamp
                        timestamps = [datetime.combine(file_date, datetime.strptime(t, '%H:%M:%S').time()) 
                                      for t in frequency_data.index]
                        power_values = frequency_data.values
                        
                        # Store the data with timestamps
                        all_data.extend(zip(timestamps, power_values))
    
    # Create a DataFrame from the collected data and sort by timestamp
    time_series_df = pd.DataFrame(all_data, columns=['Timestamp', 'Power'])
    time_series_df = time_series_df.sort_values(by='Timestamp').reset_index(drop=True)
    
    return time_series_df

def plot_gmm_and_lowest_component(df, max_components=10):
    X = df['Power'].values.reshape(-1, 1)
    best_gmm = None
    best_bic = np.inf
    best_n_components = 1
    
    # Fit GMMs with 1 to max_components components and find the best one
    for n_components in range(1, max_components + 1):
        gmm = GaussianMixture(n_components=n_components, random_state=0)
        gmm.fit(X)
        bic = gmm.bic(X)
        if bic < best_bic:
            best_bic = bic
            best_gmm = gmm
            best_n_components = n_components

    # Plot the best GMM PDF
    x = np.linspace(X.min(), X.max(), 1000).reshape(-1, 1)
    log_prob = best_gmm.score_samples(x)
    responsibilities = best_gmm.predict_proba(x)
    pdf = np.exp(log_prob)
    pdf_individual = responsibilities * pdf[:, np.newaxis]

    plt.figure(figsize=(10, 12))

    # Plot full GMM PDF and individual components
    plt.subplot(2, 1, 1)
    plt.hist(X, bins=30, density=True, alpha=0.6, color='gray', label='Data histogram')
    plt.plot(x, pdf, '-', color='black', label='GMM PDF')
    
    for i in range(best_n_components):
        plt.plot(x, pdf_individual[:, i], '--', label=f'Component {i+1}')

    plt.title(f'{start_date} to {end_date} SH2-DSL GMM PDFs for {target_frequency} GHz')
    plt.xlabel('Power (dB)')
    plt.ylabel('Density')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    
    # Find the component with the lowest mean
    lowest_mean_component = np.argmin(best_gmm.means_)
    lowest_mean_pdf = pdf_individual[:, lowest_mean_component]
    lowest_mean = best_gmm.means_[lowest_mean_component][0]
    lowest_std = np.sqrt(best_gmm.covariances_[lowest_mean_component][0][0])
    five_sigma_value = lowest_mean + 5 * lowest_std

    # Plot the lowest power value component's PDF and the 5 sigma line
    plt.subplot(2, 1, 2)
    plt.plot(x, lowest_mean_pdf, '-', color='blue', label='Lowest Mean Component PDF')
    plt.axvline(five_sigma_value, color='red', linestyle='--', label=f'5 Sigma = {five_sigma_value:.2f}')
    plt.title(f'Lowest Power Component PDF and 5 Sigma Line')
    plt.xlabel('Power (dB)')
    plt.ylabel('Density')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

# Parameters
base_folder = '/mnt/4tbssd/time_series_matrix_data/sh2'  # Replace with your base folder path
start_date = datetime(2021, 1, 1)  # Replace with your start date
end_date = datetime(2022, 12, 31)  # Replace with your end date
target_frequency = 0.4353  # Replace with the desired frequency in GHz

# Extract the data
time_series_data = extract_frequency_data(base_folder, start_date, end_date, target_frequency)

# Save to a CSV file (optional)
#time_series_data.to_csv('frequency_time_series.csv', index=False)

# Fit GMM and plot PDFs with 5 sigma line
plot_gmm_and_lowest_component(time_series_data)

