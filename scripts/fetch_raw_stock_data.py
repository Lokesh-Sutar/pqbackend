import os

import polars as pl
import requests
from tqdm import tqdm

tickers_to_extract = [
    'AAPL',
    'AMD',
    'AMZN',
    'GOOG',
    'IBM',
    'META',
    'MSFT',
    'NFLX',
    'NVDA',
    'ORCL',
    'PYPL',
    'QCOM',
    'TSLA',
    'UBER',
    'AGCO',
    'BA',
    'CTVA',
    'DE',
    'GOOGL',
    'JNJ',
    'LMT',
    'MRK',
    'NOC',
    'PFE',
    'RTX',
]

data_dir = 'stock_data_raw_parquet'
os.makedirs(data_dir, exist_ok=True)

base_url = 'https://huggingface.co/datasets/paperswithbacktest/Stocks-Daily-Price/resolve/main/data'
parquet_file_names = [
    'train-00000-of-00004.parquet',
    'train-00001-of-00004.parquet',
    'train-00002-of-00004.parquet',
    'train-00003-of-00004.parquet',
]

print('Starting Download: ')
for file_name in parquet_file_names:
    file_url = f'{base_url}/{file_name}'
    file_path = os.path.join(data_dir, file_name)
    if not os.path.exists(file_path):
        try:
            response = requests.get(file_url, stream=True)
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))
            with tqdm(
                total=total_size,
                unit='iB',
                unit_scale=True,
                desc=f'Downloading {file_name}',
            ) as progress_bar:
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        progress_bar.update(len(chunk))
        except requests.exceptions.RequestException as e:
            print(f'Failed to download {file_name}: {e}')
    else:
        print(f'Skipping {file_name} (already exists).')
print('Download Finished!\n')

downloaded_files = [
    os.path.join(data_dir, f)
    for f in parquet_file_names
    if os.path.exists(os.path.join(data_dir, f))
]
if downloaded_files:
    print('Processing Data with Polars')
    lazy_df = pl.scan_parquet(downloaded_files)
    final_lazy_df = lazy_df.filter(pl.col('symbol').is_in(tickers_to_extract)).select(
        ['symbol', 'date', 'open', 'high', 'low', 'close', 'volume', 'adj_close']
    )
    final_df = final_lazy_df.collect()
    output_dir_csv = 'ticker_csvs'
    os.makedirs(output_dir_csv, exist_ok=True)
    print(f"\nSaving individual CSV files to '{output_dir_csv}/' directory ---")

    for ticker_symbol_tuple, data in tqdm(
        final_df.group_by('symbol', maintain_order=True), desc='Saving CSVs'
    ):
        ticker_name = ticker_symbol_tuple[0]
        file_path = os.path.join(output_dir_csv, f'{ticker_name}.csv')
        data.write_csv(file_path)

    print(
        f"\nSuccessfully created separate CSV files in the '{output_dir_csv}/' directory."
    )
else:
    print('\nNo Parquet files were found. Processing step skipped.')
