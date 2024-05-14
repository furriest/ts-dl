import requests
import os, sys
from urllib.parse import urljoin

# chunks_url = "https://events-delivery-records.webinar.ru/streamer/default/storage/events-storage.webinar.ru/api-storage/files/wowza/2024/05/14/96ad6c15cc2c61e42ddec2e75002281ee1f45a896c961374f9a9f13a5d9.mp4/chunklist.m3u8"
try:
  chunks_url = sys.argv[1]
except:
  print('Usage: ', sys.argv[0], ' <URL> ')
  exit()

def download_chunk(url, file_name):
    print('Downloading', url)
    response = requests.get(url, stream=True)
    with open(file_name, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

def aggregate_files(file_list, output_file):
    with open(output_file, 'wb') as output:
        for file_name in file_list:
            with open(file_name, 'rb') as file:
                output.write(file.read())

def read_m3u8_playlist(url):
    response = requests.get(url)
    if response.status_code == 200:
        lines = response.text.strip().split('\n')
        playlist = [line for line in lines if not line.startswith('#')]
        return playlist
    else:
        print(f"Error {response.status_code}: Unable to read playlist from {url}")
        return []

# List of TS chunk URLs
ts_chunk_urls = read_m3u8_playlist(chunks_url)

# Download TS chunks
ts_chunk_files = []
for i, url in enumerate(ts_chunk_urls):
    file_name = f"chunk_{i}.ts"
    download_chunk(urljoin(chunks_url, url), file_name)
    ts_chunk_files.append(file_name)

# Aggregate TS chunks
output_file = "output.ts"
aggregate_files(ts_chunk_files, output_file)

# Clean up TS chunk files
for file_name in ts_chunk_files:
    os.remove(file_name)
