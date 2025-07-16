import pandas as pd
import os
import re # Import the regular expression module for sanitization

file_path = r'D:\My Base\Share_Analyst\B2B\B2B_summary.xlsx'
sheet_name = 'Records'
df = pd.read_excel(file_path, sheet_name=sheet_name)
df = pd.DataFrame(df)
df_col = df.columns.tolist()

def create_folders_from_dataframe(df: pd.DataFrame, base_path: str = r"D:\My Base\Share_Analyst\B2B\CASES"):
    """
    Creates folders based on 'CASE TITLE' column values from a DataFrame,
    only for rows where the 'REPORTED' column is 'ME'.

    Args:
        df (pd.DataFrame): The input DataFrame containing 'CASE TITLE' and 'REPORTED' columns.
        base_path (str): The base directory where new folders will be created.
                         Defaults to 'D:\My Base\Share_Analyst\B2B\CASES'.
    """
    print(f"Attempting to create folders in: {base_path}")

    # Ensure the base path exists
    os.makedirs(base_path, exist_ok=True)

    # Filter the DataFrame for rows where 'REPORTED' column is 'ME'
    # .str.upper() is used for case-insensitive matching of "ME"
    # .dropna() removes any rows where 'CASE TITLE' might be NaN, which would cause an error
    filtered_df = df[df['REPORTED'].astype(str).str.upper() == 'ME'].copy()

    if 'CASE TITLE' not in filtered_df.columns:
        print("Error: 'CASE TITLE' column not found in the filtered DataFrame.")
        return
    if filtered_df.empty:
        print("No cases REPORTED by 'ME' found to create folders for.")
        return

    # Define invalid characters for Windows folder names
    # (/, \, :, *, ?, ", <, >, |)
    # Using a regex pattern to replace them with an underscore or remove them
    invalid_chars_pattern = re.compile(r'[\\/:*?"<>|]')

    # Iterate over the unique 'CASE TITLE' values in the filtered DataFrame
    for case_title in filtered_df['CASE TITLE'].unique():
        if pd.isna(case_title): # Skip NaN values in 'CASE TITLE'
            continue

        # Convert to string and strip leading/trailing whitespace
        folder_name_raw = str(case_title).strip()

        # Sanitize the folder name: replace invalid characters with an underscore
        # You could also choose to remove them: folder_name = invalid_chars_pattern.sub('', folder_name_raw)
        folder_name = invalid_chars_pattern.sub('_', folder_name_raw)

        # Ensure the folder name is not empty after sanitization
        if not folder_name:
            print(f"Warning: Sanitized folder name for '{case_title}' resulted in an empty string. Skipping.")
            continue

        # Construct the full path for the new folder
        folder_path = os.path.join(base_path, folder_name)

        try:
            # Create the directory. exist_ok=True prevents an error if the directory already exists.
            os.makedirs(folder_path, exist_ok=True)
            if os.path.exists(folder_path):
                print(f"Folder created or already exists: '{folder_path}'")
            else:
                # This else block might be hit if os.makedirs fails for other reasons
                # but doesn't raise an exception (e.g., permission issues without explicit error)
                print(f"Failed to confirm folder creation for: '{folder_path}'")
        except OSError as e:
            print(f"Error creating folder '{folder_path}': {e}")

if __name__ == "__main__":

    # Call the function to create folders based on the DataFrame
    create_folders_from_dataframe(df, base_path=r"D:\My Base\Share_Analyst\B2B\CASES")

