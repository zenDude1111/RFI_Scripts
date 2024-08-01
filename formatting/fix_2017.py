import pandas as pd
import os
import csv
from tempfile import NamedTemporaryFile
import shutil

# Load the specific file and extract the first column and header
specific_file_path = '/media/polarbear/586CF6E16CF6B8B8/sh2/2018/20180101_matrix.csv'  # Replace with the actual file path
specific_df = pd.read_csv(specific_file_path)
first_column = specific_df.iloc[:, 0].tolist()
header = specific_df.columns.tolist()

# Directory containing the 2017 files
directory_path = '/media/polarbear/586CF6E16CF6B8B8/sh2/2017'  # Replace with the actual directory path

def update_file(file_path, first_column, header):
    # Create a temporary file
    temp_file = NamedTemporaryFile(delete=False, mode='w', newline='')
    
    with open(file_path, 'r', newline='') as csv_file, temp_file:
        reader = csv.reader(csv_file)
        writer = csv.writer(temp_file)
        
        # Write the header from the specific file
        writer.writerow(header)
        
        for i, row in enumerate(reader):
            # Skip the original header row
            if i == 0:
                continue
            # Replace the first column with the values from the specific file's first column
            if i <= len(first_column):
                row[0] = first_column[i - 1]  # Adjust index because of skipping header
            writer.writerow(row)
    
    # Move the temp file to replace the original file
    shutil.move(temp_file.name, file_path)

# Iterate through all files with "2017" in their name
for filename in os.listdir(directory_path):
    if '20170124' in filename and filename.endswith('.csv'):
        file_path = os.path.join(directory_path, filename)
        update_file(file_path, first_column, header)
        print(f"{filename} has been updated.")

print("All 2017 files have been updated with the first column and header from the specific file.")



