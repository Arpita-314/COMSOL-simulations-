import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
import scipy.interpolate
from tkinter import filedialog

# Function to recursively find all CSV files in a directory and subdirectories
def find_csv_files(directory):
    """
    Recursively finds all CSV files in the given directory and subdirectories.

    Parameters:
    - directory (str): The directory path where to look for CSV files.

    Returns:
    - csv_files (list): A list of paths to CSV files.
    """
    csv_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.csv'):
                csv_files.append(os.path.join(root, file))
    if not csv_files:
        print("No CSV files found in the directory and its subdirectories.")
    return csv_files

# Function to select a directory using GUI
def select_directory():
    """
    Opens a GUI dialog to select a directory and returns the selected path.

    Returns:
    - directory (str): The selected directory path.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    root.attributes('-topmost', True)  # Bring the dialog to the front
    directory = filedialog.askdirectory(title="Select Directory Containing CSV Files")
    root.destroy()
    return directory

# Main function to execute the script
def main():
    """
    Main function to execute the script.
    """
    # Select the directory using GUI
    directory = select_directory()

    if not directory:
        print("No directory selected. Exiting.")
        sys.exit(1)

    # Normalize the path to handle any issues with slashes
    directory = os.path.normpath(directory)

    if not os.path.isdir(directory):
        print(f"The directory '{directory}' does not exist.")
        sys.exit(1)

    # Create a folder for plots within the selected directory
    plot_folder = os.path.join(directory, "plots")
    os.makedirs(plot_folder, exist_ok=True)

    # Find all CSV files in the directory and subdirectories
    csv_files = find_csv_files(directory)
    if not csv_files:
        sys.exit(1)  # Exit if no CSV files are found

    # Define a list to keep track of different material data for plotting
    material_data = []
    consolidated_data = {
        'S11': {},
        'S12': {},
        'S21': {},
        'S22': {},
        'Z11': {},
        'Z12': {},
        'Z21': {},
        'Z22': {},
        'TDR-Impedance': {},
        'Z0': {}
    }  # To keep track of consolidated S-parameter, Z-parameter, TDR-Impedance, and Z0 vs height data

    # Process each CSV file
    for csv_path in csv_files:
        try:
            # Load the CSV data using pandas
            print(f"Loading CSV file: {os.path.basename(csv_path)}")
            data = pd.read_csv(csv_path)

            # Extract frequency and convert from MHz to GHz
            if 'Freq [MHz]' in data.columns:
                frequency = data['Freq [MHz]'] / 1000.0  # Convert MHz to GHz
            else:
                print(f"No frequency column found in '{csv_path}'. Skipping.")
                continue

            # Identify S-parameter columns
            s_parameters = {
                'S11': 'dB(St(1,1)) []',
                'S12': 'dB(St(1,2)) []',
                'S21': 'dB(St(2,1)) []',
                'S22': 'dB(St(2,2)) []'
            }

            # Extract height from the folder name (assuming folder names are like '200', '400', etc.)
            height_folder = os.path.basename(os.path.dirname(csv_path))
            try:
                height = int(height_folder.replace('nm', ''))  # Directly extract height from folder name
                print(f"Extracted height: {height} nm from folder: {height_folder}")  # Debugging output
            except ValueError:
                print(f"Warning: Couldn't determine height from folder name '{height_folder}'. Skipping...")
                continue

            # Process each S-parameter column if it exists
            for param, column_name in s_parameters.items():
                if column_name in data.columns:
                    s_param_data = data[column_name]

                    # Store data for averaging across multiple tries
                    material = os.path.dirname(csv_path).split(os.sep)[-3]  # Use grandparent folder name as material identifier
                    if param not in consolidated_data:
                        consolidated_data[param] = {}
                    if material not in consolidated_data[param]:
                        consolidated_data[param][material] = {}
                    if height not in consolidated_data[param][material]:
                        consolidated_data[param][material][height] = []
                    consolidated_data[param][material][height].append((frequency, s_param_data))

        except pd.errors.EmptyDataError:
            print(f"Warning: The file '{csv_path}' is empty or contains only headers. Skipping.")
        except pd.errors.ParserError as e:
            print(f"Error parsing '{csv_path}': {e}. Skipping.")
        except Exception as e:
            print(f"Error processing '{csv_path}': {e}. Skipping.")

    # Plot S11, S12, S21, S22 parameter against frequency for each material with different heights
    for param in ['S11', 'S12', 'S21', 'S22']:
        for material, height_data in consolidated_data[param].items():
            plt.figure(figsize=(10, 6), dpi=400)  # Set the DPI to 400 for high resolution

            # Iterate over each height and plot the average frequency response
            for height, data_list in sorted(height_data.items()):
                # Average the data from multiple tries
                if len(data_list) > 1:
                    avg_frequency = data_list[0][0]  # Assuming all tries have the same frequency values
                    avg_s_param_values = np.mean([s_param.values for _, s_param in data_list], axis=0)
                else:
                    avg_frequency, avg_s_param_values = data_list[0]

                plt.plot(avg_frequency, avg_s_param_values, label=f'Height: {height} nm')

            # Labels and legend
            plt.xlabel('Frequency (GHz)')
            plt.ylabel(f'{param} Parameter (dB)')
            # plt.title(f'{param} vs Frequency for {material} (Multi-Line Plot for Different Heights)')
            plt.legend(loc='upper right')

            # Save the consolidated (multi-line) plot
            consolidated_plot_path = os.path.join(plot_folder, f"{param}_vs_frequency_{material}.png")
            plt.savefig(consolidated_plot_path)
            plt.show()
            plt.close()
            print(f"Consolidated (Multi-Line) {param} vs Frequency plot saved: {consolidated_plot_path}")

    # Create summary tables for each S-parameter and material combination
    for param in ['S11', 'S12', 'S21', 'S22']:
        for material, height_data in consolidated_data[param].items():
            summary_data = []
            for height, data_list in height_data.items():
                # Average the data from multiple tries
                if len(data_list) > 1:
                    avg_s_param_values = np.mean([s_param.values for _, s_param in data_list], axis=0)
                else:
                    _, avg_s_param_values = data_list[0]
                max_value = avg_s_param_values.max()
                min_value = avg_s_param_values.min()
                summary_data.append([height, max_value, min_value])

            summary_df = pd.DataFrame(summary_data, columns=['Height (nm)', 'Max Value (dB)', 'Min Value (dB)'])
            summary_path = os.path.join(plot_folder, f"summary_{param}_impedance_match_{material}.csv")
            summary_df.to_csv(summary_path, index=False)
            print(f"Summary table for {param} and {material} saved: {summary_path}")

if __name__ == '__main__':
    main()
# import os
# import pandas as pd
# import matplotlib.pyplot as plt
# import tkinter as tk
# from tkinter import filedialog

# def find_csv_files(directory):
#     """
#     Recursively finds all CSV files in the given directory and subdirectories.

#     Parameters:
#     - directory (str): The directory path where to look for CSV files.

#     Returns:
#     - csv_files (list): A list of paths to CSV files.
#     """
#     csv_files = []
#     for root, dirs, files in os.walk(directory):
#         for file in files:
#             if file.lower().endswith('.csv'):
#                 csv_files.append(os.path.join(root, file))
#     if not csv_files:
#         print("No CSV files found in the directory and its subdirectories.")
#     return csv_files

# def select_directory():
#     """
#     Opens a GUI dialog to select a directory and returns the selected path.

#     Returns:
#     - directory (str): The selected directory path.
#     """
#     root = tk.Tk()
#     root.withdraw()  # Hide the main window
#     directory = filedialog.askdirectory()
#     return directory

# def load_and_plot_data(directory, columns):
#     """
#     Loads CSV files from the directory, extracts the specified columns, and plots them in different subplots.

#     Parameters:
#     - directory (str): The directory path where the CSV files are located.
#     - columns (list): List of column names to plot.
#     """
#     csv_files = find_csv_files(directory)
#     data_dict = {col: [] for col in columns}
#     labels_dict = {col: [] for col in columns}

#     for csv_path in csv_files:
#         try:
#             # Load the CSV data using pandas
#             data = pd.read_csv(csv_path)

#             # Extract height from the folder name (assuming folder names are like '200', '400', etc.)
#             height_folder = os.path.basename(os.path.dirname(csv_path))

#             # Print name of file and its directory
#             print(f"Reading file: {csv_path}")

#             # Extract specified columns
#             for col in columns:
#                 if col in data.columns:
#                     data_dict[col].append(data[col].values)
#                     labels_dict[col].append(height_folder)
#                 else:
#                     print(f"No {col} column found in '{csv_path}'. Skipping.")
#         except Exception as e:
#             print(f"Error reading '{csv_path}': {e}")
#             continue

#     # Plot the data in different subplots
#     fig, axs = plt.subplots(len(columns), 1, figsize=(10, 6 * len(columns)))

#     for i, col in enumerate(columns):
#         if data_dict[col]:
#             for data, label in zip(data_dict[col], labels_dict[col]):
#                 axs[i].plot(data, label=label)
#             axs[i].set_title(f'{col} Parameter')
#             axs[i].set_xlabel('Index')
#             axs[i].set_ylabel(col)
#             axs[i].legend()

#     plt.tight_layout()
#     plt.show()

# if __name__ == "__main__":
#     print("Select directory for loading CSV files:")
#     directory = select_directory()
#     if directory:
#         columns = ["]", "dB(St(2,1)) []", "dB(St(1,2)) []", "dB(St(1,1)) []", "dB(St(2,2)) []"]
#         load_and_plot_data(directory, columns)
#     else:
#         print("No directory selected. Exiting.")