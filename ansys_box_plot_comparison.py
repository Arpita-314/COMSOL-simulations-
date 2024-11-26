import os
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog

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

def select_directory():
    """
    Opens a GUI dialog to select a directory and returns the selected path.

    Returns:
    - directory (str): The selected directory path.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    directory = filedialog.askdirectory()
    return directory

def load_and_plot_s21(directory, s_parameter="dB(St(2,1)) []"):
    """
    Loads CSV files from the directory, extracts the S21 parameter, and plots a box plot.

    Parameters:
    - directory (str): The directory path where the CSV files are located.
    - s_parameter (str): The S-parameter to plot (default is 'S21').
    """
    csv_files = find_csv_files(directory)
    s21_data = []

    for csv_path in csv_files:
        try:
            # Load the CSV data using pandas
            data = pd.read_csv(csv_path)

            # Print name of file and its directory
            print(f"Reading file: {csv_path}")

            # Extract S21 parameter
            if s_parameter in data.columns:
                s21_data.append(data[s_parameter])
            else:
                print(f"No {s_parameter} column found in '{csv_path}'. Skipping.")
                continue
        except Exception as e:
            print(f"Error reading '{csv_path}': {e}")
            continue

    # Plot the box plot for S21 parameter
    plt.figure(figsize=(10, 6))
    plt.boxplot(s21_data, labels=[os.path.basename(directory)] * len(s21_data))
    plt.title(f'Box Plot of {s_parameter} Parameter')
    plt.xlabel('Files')
    plt.ylabel(s_parameter)
    plt.show()

if __name__ == "__main__":
    directories = []
    for i in range(5):
        print(f"Select directory {i+1} for loading CSV files:")
        directory = select_directory()
        if directory:
            directories.append(directory)
        else:
            print("No directory selected. Exiting.")
            exit()

    for directory in directories:
        load_and_plot_s21(directory)