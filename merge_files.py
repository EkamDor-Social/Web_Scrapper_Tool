import os
import glob
import shutil
import pandas as pd
import pickle
from datetime import datetime

def merge_csv_and_clean_pickle():
    # Get all CSV files in current directory
    csv_files = glob.glob('*.csv')
    if not csv_files:
        print("No CSV files found in current directory")
        return

    print(f"Found {len(csv_files)} CSV files")

    # Read and combine all CSV files
    dfs = []
    for file in csv_files:
        df = pd.read_csv(file)
        dfs.append(df)
        print(f"Read {file}: {len(df)} rows")

    # Combine all dataframes
    combined_df = pd.concat(dfs, ignore_index=True)
    print(f"Combined total: {len(combined_df)} rows")

    # Remove rows where 'timestamp' column is empty/NaN
    if 'timestamp' in combined_df.columns:
        # Drop NaN and empty strings
        combined_df = combined_df.dropna(subset=['timestamp'])
        combined_df = combined_df[combined_df['timestamp'].astype(str).str.strip() != '']

        # Convert timestamp to datetime and sort
        combined_df['timestamp'] = pd.to_datetime(combined_df['timestamp'])
        combined_df = combined_df.sort_values('timestamp', ascending=True).reset_index(drop=True)

        print(f"After removing empty timestamps: {len(combined_df)} rows")
        print(f"Timestamp range: {combined_df['timestamp'].min()} to {combined_df['timestamp'].max()}")
    else:
        print("Warning: 'timestamp' column not found")

    # Save combined dataframe to pickle
    timestamp_str = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    os.makedirs('merged_pkl', exist_ok=True)

    output_pkl = f'merged_pkl/combined_data_{timestamp_str}.pkl'
    combined_df.to_pickle(output_pkl)
    print(f"Saved combined data to {output_pkl}")

    # Get all URLs from the combined dataframe
    if 'url' in combined_df.columns:
        urls_in_csv = set(combined_df['url'].dropna().astype(str))
        print(f"Found {len(urls_in_csv)} unique URLs in CSV files")
    else:
        print("Warning: 'url' column not found")
        urls_in_csv = set()

    # Process fixed pickle file: seen_urls.pkl
    pkl_file = 'seen_urls.pkl'
    if os.path.exists(pkl_file):
        try:
            with open(pkl_file, 'rb') as f:
                data = pickle.load(f)
            if isinstance(data, dict):
                original_count = len(data)
                # Remove URLs that are in the CSV files
                keys_to_remove = [key for key in data.keys() if key in urls_in_csv]
                for key in keys_to_remove:
                    del data[key]
                # Save back with same name
                with open(pkl_file, 'wb') as f:
                    pickle.dump(data, f)
                print(f"Updated {pkl_file}: removed {len(keys_to_remove)} URLs ({original_count} → {len(data)} entries)")
            else:
                print(f"Skipping {pkl_file}: not a dictionary")
        except Exception as e:
            print(f"Error processing {pkl_file}: {e}")
    else:
        print(f"{pkl_file} not found; skipping pickle cleanup")

    # Move used CSV files to combined_csv folder
    if csv_files:
        os.makedirs('combined_csv', exist_ok=True)
        
        for file in csv_files:
            src = file
            dst = os.path.join('combined_csv', file)
            shutil.move(src, dst)
        print(f"Moved {len(csv_files)} CSV files to 'combined_csv/'")

if __name__ == "__main__":
    merge_csv_and_clean_pickle()