import os
import pandas as pd

base_path = r"C:\Users\91901\Downloads\data"

ghi_path = os.path.join(base_path, 'GHI')
pr_path = os.path.join(base_path, 'PR')

def load_data(folder, value_column_name):
    data_frames = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.lower().endswith('.csv'):
                file_path = os.path.join(root, file)
                try:
                    df = pd.read_csv(file_path)
                    df.columns = [c.strip().lower() for c in df.columns]
                    if 'date' in df.columns and value_column_name.lower() in df.columns:
                        data_frames.append(df[['date', value_column_name.lower()]])
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    if data_frames:
        merged = pd.concat(data_frames, ignore_index=True)
        merged = merged.drop_duplicates(subset='date')
        return merged
    return pd.DataFrame(columns=['date', value_column_name.lower()])

# Load both datasets
print("Loading GHI data...")
ghi_df = load_data(ghi_path, 'GHI')

print("Loading PR data...")
pr_df = load_data(pr_path, 'PR')

# Merge them on 'date'
print("Merging on 'date'...")
final_df = pd.merge(ghi_df, pr_df, on='date', how='outer')

# Optional: Sort by date
final_df = final_df.sort_values('date')

# Save to CSV
final_df.to_csv('merged_ghi_pr.csv', index=False)
print("Done: Saved as 'merged_ghi_pr.csv'")
