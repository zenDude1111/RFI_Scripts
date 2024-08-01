import os
import requests
import tarfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from bs4 import BeautifulSoup

# URL of the website
URL = "http://bicep.rc.fas.harvard.edu/southpole_info/EMI_WG/keckdaq/signalhound2/"

def download_file(url, path):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        total_size_in_bytes = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 Kibibyte

        with open(path, 'wb') as file:
            for data in response.iter_content(block_size):
                file.write(data)
        print(f"Download completed for {path}")
    except requests.RequestException as e:
        print(f"Error downloading {url}: {e}")
        if os.path.exists(path):
            os.remove(path)

def unpack_and_delete_tar(tar_path, save_directory):
    try:
        print(f"Unpacking {tar_path}...")
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=save_directory)
        print(f"Unpacked {tar_path}")
    except tarfile.TarError as e:
        print(f"Error unpacking {tar_path}: {e}")
    finally:
        if os.path.exists(tar_path):
            os.remove(tar_path)
            print(f"Deleted {tar_path}")

def download_and_process(url, link, save_directory):
    tar_path = os.path.join(save_directory, link)
    download_file(url + link, tar_path)
    unpack_and_delete_tar(tar_path, save_directory)

def download_and_unpack_tar(url, save_directory, start_date_str, end_date_str):
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        tar_links = [a['href'] for a in soup.find_all('a') if a['href'].endswith('.tar.gz')]
    except requests.RequestException as e:
        print(f"Error retrieving URL {url}: {e}")
        return

    # Convert the start_date_str and end_date_str to datetime objects
    start_date = datetime.strptime(start_date_str, '%Y%m%d')
    end_date = datetime.strptime(end_date_str, '%Y%m%d')

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for link in tar_links:
            try:
                # Extract the date part from the filename
                file_date = datetime.strptime(link[:8], '%Y%m%d')
                # Check if the file_date is after the start_date and before or equal to the end_date
                if start_date < file_date <= end_date:
                    futures.append(executor.submit(download_and_process, url, link, save_directory))
            except ValueError:
                # Handle the error or log it as necessary
                continue

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error in concurrent processing: {e}")

# Example usage
save_dir = '/media/polarbear/586CF6E16CF6B8B81/2024/sh2'
start_date_str = '20240603'  # Example start date in YYYYMMDD format
end_date_str = '20240711'  # Example end date in YYYYMMDD format
download_and_unpack_tar(URL, save_dir, start_date_str, end_date_str)



