import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the results CSV file
input_file = '/home/polarbear/Desktop/erics_code/seasonal_metrics/csvs/seasonal_stats_sh2_Kurtosis.csv'
data = pd.read_csv(input_file)

# Set the significance level
alpha = 0.05

# Extract frequency and p-value columns
frequencies = data['Frequency (GHz)']
p_values = data['P-value']

# Convert P-values to numeric, handling any non-numeric entries like '< 1e-10'
p_values = pd.to_numeric(p_values, errors='coerce')

# Plotting the p-values
plt.figure(figsize=(10, 6))
plt.scatter(frequencies, p_values, label='P-values', color='blue')

# Highlight significant p-values
significant = p_values < alpha
plt.scatter(frequencies[significant], p_values[significant], color='red', label='Significant (p < 0.05)')

# Add horizontal line for alpha level
plt.axhline(y=alpha, color='gray', linestyle='--', label='Significance Threshold (0.05)')

# Add labels and title
plt.xlabel('Frequency (GHz)')
plt.ylabel('P-value')
plt.title('SH2-DSL Kurtosis P-values of Seasonal Differences Across Frequency Bins')
plt.yscale('log')  # Use log scale for better visibility of small p-values
plt.grid(True)
plt.legend()

# Set x-axis ticks every 0.5 GHz
plt.xticks(np.arange(min(frequencies), max(frequencies) + 0.5, 0.5))

# Show the plot
plt.tight_layout()
plt.show()