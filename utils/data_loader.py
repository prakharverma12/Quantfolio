import pandas as pd

def load_transaction_files(file_list):
    # Read and concatenate all files
    dfs = [pd.read_csv(f) for f in file_list]
    merged_df = pd.concat(dfs, ignore_index=True)

    # Convert 'Date/Time' to datetime type
    merged_df['Date/Time'] = pd.to_datetime(merged_df['Date/Time'], errors='coerce')

    # Sort by datetime
    merged_df = merged_df.sort_values(by='Date/Time').reset_index(drop=True)

    return merged_df
