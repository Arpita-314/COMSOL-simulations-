# -- coding: utf-8 --
"""
Created on 2023-10-15

@author: go29lap
"""

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

# Function to list all CSV files in the directory
def list_csv_files(directory):
    """
    Lists all CSV files in the given directory.

    Parameters:
    - directory (str): The directory path where to look for CSV files.

    Returns:
    - files (list): A list of CSV filenames.
    """
    files = [f for f in os.listdir(directory) if f.lower().endswith('.csv')]
    if not files:
        print("No CSV files found in the directory.")
        return []
    return files

# Function to ask the user for the file they want to plot
def ask_user_for_file(files):
    """
    Prompts the user to select a file from the list.

    Parameters:
    - files (list): A list of filenames.

    Returns:
    - selected_file (str): The filename selected by the user.
    """
    print("\nAvailable CSV files:")
    for idx, file in enumerate(files):
        print(f"{idx + 1}. {file}")

    while True:
        try:
            choice = int(input("\nEnter the number of the CSV file you want to plot: "))
            if 1 <= choice <= len(files):
                return files[choice - 1]
            else:
                print("Invalid choice, please select a number from the list.")
        except ValueError:
            print("Invalid input, please enter a number.")

# Function to ask the user for the scaling type (log or linear)
def ask_plot_scale(axis_name='X'):
    """
    Asks the user to select the scale type for an axis.

    Parameters:
    - axis_name (str): Name of the axis ('X' or 'Y').

    Returns:
    - scale (str): The scale type selected by the user ('linear' or 'log').
    """
    print(f"\nSelect the scale for the {axis_name}-axis:")
    print("1. Linear scale")
    print("2. Logarithmic scale")

    while True:
        choice = input("Enter your choice (1 or 2): ")
        if choice == '1':
            return 'linear'
        elif choice == '2':
            return 'log'
        else:
            print("Invalid choice. Please enter 1 for Linear scale or 2 for Logarithmic scale.")

# Function to ask the user to select columns for X and Y axes
def ask_user_for_columns(columns):
    """
    Prompts the user to select columns for the X and Y axes.

    Parameters:
    - columns (list): A list of column names.

    Returns:
    - x_column (str): The column name selected for the X-axis.
    - y_column (str): The column name selected for the Y-axis.
    """
    print("\nAvailable columns:")
    for idx, column in enumerate(columns):
        print(f"{idx + 1}. {column}")
    while True:
        try:
            x_choice = int(input("Select the number for the X-axis column: ")) - 1
            y_choice = int(input("Select the number for the Y-axis column: ")) - 1
            if 0 <= x_choice < len(columns) and 0 <= y_choice < len(columns):
                return columns[x_choice], columns[y_choice]
            else:
                print("Invalid choice, please select numbers from the list.")
        except ValueError:
            print("Invalid input, please enter numbers.")

# Function to plot data from DataFrame
def plot_data(data, x_column, y_column, title, x_scale='linear', y_scale='linear', x_label=None, y_label=None):
    """
    Plots the specified data columns with given scaling options and saves the plot as a TIFF file.

    Parameters:
    - data (DataFrame): The DataFrame containing the data.
    - x_column (str): The name of the column for the x-axis.
    - y_column (str): The name of the column for the y-axis.
    - title (str): The title of the plot.
    - x_scale (str): The scale for the x-axis ('linear' or 'log').
    - y_scale (str): The scale for the y-axis ('linear' or 'log').
    - x_label (str): The label for the x-axis.
    - y_label (str): The label for the y-axis.
    """
    if x_column in data.columns and y_column in data.columns:
        plt.figure(figsize=(10, 6))
        plt.plot(data[x_column], data[y_column], marker='o', label=y_column)
        plt.xscale(x_scale)
        plt.yscale(y_scale)
        plt.xlabel(x_label if x_label else x_column)
        plt.ylabel(y_label if y_label else y_column)
        plt.title(title)
        plt.grid(True)
        plt.legend()

        # Ask user if they want to save the plot
        save_choice = input("Do you want to save the plot? (y/n): ")
        if save_choice.lower() == 'y':
            # Ask for filename
            save_filename = input("Enter the filename to save the plot (e.g., plot.tiff): ")
            if not save_filename.lower().endswith('.tiff'):
                save_filename += '.png'
            # Save the plot as TIFF with high DPI
            plt.savefig(save_filename, format='png', dpi=300)
            print(f"Plot saved as {save_filename}")
        else:
            # Show the plot
            plt.show()
    else:
        print(f"The required columns ({x_column} and {y_column}) do not exist in the data.")

# Function to plot the selected CSV file
def plot_csv_file(file_path):
    """
    Reads the CSV file and initiates the plotting process.

    Parameters:
    - file_path (str): The full path to the CSV file.
    """
    try:
        data = pd.read_csv(file_path)

        # Display the available columns in the CSV file
        print("\nColumns found in the file:", data.columns.tolist())

        # Ask the user to select columns for X and Y axes
        x_column, y_column = ask_user_for_columns(data.columns.tolist())

        # Ask for plot scaling
        x_scale = ask_plot_scale('X')
        y_scale = ask_plot_scale('Y')

        # Plot the data
        plot_title = f"Plot of {y_column} vs {x_column}"
        plot_data(data, x_column, y_column, plot_title, x_scale, y_scale, x_column, y_column)

    except Exception as e:
        print(f"Error reading or plotting the file: {e}")

def main():
    """
    Main function to execute the script.
    """
    # Get the current directory
    directory = os.getcwd()

    # List all CSV files in the directory
    files = list_csv_files(directory)
    if not files:
        sys.exit(1)  # Exit if no CSV files are found

    # Ask the user to select a CSV file
    selected_file = ask_user_for_file(files)
    file_path = os.path.join(directory, selected_file)

    # Plot the selected CSV file
    plot_csv_file(file_path)

