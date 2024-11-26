import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
import scipy.interpolate
from tkinter import filedialog

# ---------------------------- Helper Functions ---------------------------- #

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

# ---------------------------- Data Preparation ---------------------------- #

# Removed the averaging function since averaging of tries is not needed anymore

# ---------------------------- Plotting Functions ---------------------------- #

# Function to create multi-line consolidated data for analysis
def create_multiline_plots(directory, s_parameters, plot_folder):
    """
    Creates multi-line plots of the S-parameter data for each material and height.

    Parameters:
    - directory (str): The directory path where the CSV files are located.
    - s_parameters (dict): Dictionary of S-parameter names to column names.
    - plot_folder (str): Directory where the consolidated plots should be saved.
    """
    consolidated_data = {param: {} for param in s_parameters.keys()}

    csv_files = find_csv_files(directory)
    for csv_path in csv_files:
        try:
            # Load the CSV data using pandas
            data = pd.read_csv(csv_path)

            # Print name of file and its directory
            print(f"Reading file: {csv_path}")

            # Extract frequency and convert from MHz to GHz
            if 'Freq [MHz]' in data.columns:
                frequency = data['Freq [MHz]'] / 1000.0  # Convert MHz to GHz
            else:
                print(f"No frequency column found in '{csv_path}'. Skipping.")
                continue

            # Extract height from the folder name (assuming folder names are like '200', '400', etc.)
            height_folder = os.path.basename(os.path.dirname(csv_path))
            try:
                height = int(height_folder.replace('nm', ''))  # Directly extract height from folder name
            except ValueError:
                print(f"Warning: Couldn't determine height from folder name '{height_folder}'. Skipping...")
                continue

            # Extract material name from the path
            material = os.path.dirname(csv_path).split(os.sep)[-3]

            # Process each S-parameter column if it exists
            for param, column_name in s_parameters.items():
                if column_name in data.columns:
                    s_param_data = data[column_name]
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

    # Section 1: Plot multi-line S-parameters for different heights of the same material
    for param in s_parameters.keys():
        for material, height_data in consolidated_data[param].items():
            plt.figure(figsize=(10, 6), dpi=400)  # Set the DPI to 400 for high resolution

            # Iterate over each height and plot the data
            for height, data_list in sorted(height_data.items()):
                # Plot the data from multiple tries without averaging
                for frequency, s_param_values in data_list:
                    plt.plot(frequency, s_param_values, label=f'Height: {height} nm')

            # Labels and legend
            plt.xlabel('Frequency (GHz)')
            plt.ylabel(f'{param} Parameter (dB)')
            plt.title(f'{param} vs Frequency for {material} (Multi-Line Plot for Different Heights)')
            plt.legend(loc='upper right')

            # Save the multi-line plot
            consolidated_plot_path = os.path.join(plot_folder, f"{param}vs_frequency{material}_multiline_heights.png")
            plt.savefig(consolidated_plot_path)
            plt.close()
            print(f"Multi-Line {param} vs Frequency plot for different heights saved: {consolidated_plot_path}")
    # plt.show()

    # Section 2: Plot multi-line S-parameters for the same height across different materials
    for param in s_parameters.keys():
        for height in sorted(set(height for material_data in consolidated_data[param].values() for height in material_data.keys())):
            plt.figure(figsize=(10, 6), dpi=400)  # Set the DPI to 400 for high resolution

            # Iterate over each material and plot the data for the same height
            for material, height_data in consolidated_data[param].items():
                if height in height_data:
                    for frequency, s_param_values in height_data[height]:
                        plt.plot(frequency, s_param_values, label=f'Material: {material}')

            # Labels and legend
            plt.xlabel('Frequency (GHz)')
            plt.ylabel(f'{param} Parameter (dB)')
            plt.title(f'{param} vs Frequency for Height {height} nm (Multi-Line Plot for Different Materials)')
            plt.legend(loc='upper right')

            # Save the multi-line plot
            consolidated_plot_path = os.path.join(plot_folder, f"{param}vs_frequency_height{height}_multiline_materials.png")
            plt.savefig(consolidated_plot_path)
            # plt.show()
            plt.close()
            print(f"Multi-Line {param} vs Frequency plot for different materials saved: {consolidated_plot_path}")

# Function to create summary tables for each S-parameter and material combination
def create_summary_tables(consolidated_data, plot_folder, s_parameters):
    """
    Creates summary tables for each S-parameter and material combination.

    Parameters:
    - consolidated_data (dict): Consolidated data for each material, parameter, and height.
    - plot_folder (str): Path to the folder where summary tables will be saved.
    - s_parameters (dict): Dictionary of S-parameter names to column names.
    """
    for param in s_parameters.keys():
        for material, height_data in consolidated_data[param].items():
            if material == 'Ti-Au':  # Only create summary for Ti-Au
                summary_data = []
                for height, data_list in height_data.items():
                    # Calculate the maximum and minimum for each try without averaging
                    for frequency, s_param_values in data_list:
                        max_value = s_param_values.max()
                        min_value = s_param_values.min()
                        summary_data.append([height, max_value, min_value])

                summary_df = pd.DataFrame(summary_data, columns=['Height (nm)', 'Max Value (dB)', 'Min Value (dB)'])
                summary_path = os.path.join(plot_folder, f"summary_{param}impedance_match{material}.csv")
                summary_df.to_csv(summary_path, index=False)
                print(f"Summary table for {param} and {material} saved: {summary_path}")

# Function to create box plots for each S-parameter and material combination
def create_box_plots(consolidated_data, plot_folder, s_parameters):
    """
    Creates box plots for each S-parameter and material combination.

    Parameters:
    - consolidated_data (dict): Consolidated data for each material, parameter, and height.
    - plot_folder (str): Path to the folder where box plots will be saved.
    - s_parameters (dict): Dictionary of S-parameter names to column names.
    """
    for param in s_parameters.keys():
        for material, height_data in consolidated_data[param].items():
            plt.figure(figsize=(10, 6), dpi=400)
            data_to_plot = []
            labels = []
            for height, data_list in sorted(height_data.items()):
                # Append each try's data without averaging
                for _, s_param_values in data_list:
                    data_to_plot.append(s_param_values)
                    labels.append(f'Height: {height} nm')

            plt.boxplot(data_to_plot, labels=labels)
            plt.xlabel('Height (nm)')
            plt.ylabel(f'{param} Parameter (dB)')
            plt.title(f'Box Plot of {param} for {material}')

            # Save the box plot
            box_plot_path = os.path.join(plot_folder, f"box_plot_{param}_{material}.png")
            # plt.savefig(box_plot_path)
            plt.show()
            # plt.close()
            print(f"Box plot for {param} and {material} saved: {box_plot_path}")
    # plt.show()

# Function to create radar plots for each S-parameter and material combination
def create_radar_plots(consolidated_data, plot_folder, s_parameters):
    """
    Creates radar plots for each S-parameter and material combination.

    Parameters:
    - consolidated_data (dict): Consolidated data for each material, parameter, and height.
    - plot_folder (str): Path to the folder where radar plots will be saved.
    - s_parameters (dict): Dictionary of S-parameter names to column names.
    """
    labels = list(s_parameters.keys())
    num_vars = len(labels)

    for material in consolidated_data['S11'].keys():  # Assuming 'S11' exists for all materials
        values = []
        for param in labels:
            param_values = []
            for height, data_list in consolidated_data[param][material].items():
                # Calculate average for each height without averaging the tries
                for _, s_param_values in data_list:
                    avg_value = s_param_values.mean()
                    param_values.append(avg_value)
            values.append(np.mean(param_values))

        values += values[:1]
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        angles += angles[:1]

        plt.figure(figsize=(6, 6), dpi=400)
        ax = plt.subplot(111, polar=True)
        ax.fill(angles, values, color='skyblue', alpha=0.4)
        ax.plot(angles, values, color='blue', linewidth=2)
        ax.set_yticklabels([])
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels)
        plt.title(f'Radar Plot for {material}')

        # Save the radar plot
        radar_plot_path = os.path.join(plot_folder, f"radar_plot_{material}.png")
        # plt.savefig(radar_plot_path)
        plt.show()
        # plt.close()
        print(f"Radar plot for {material} saved: {radar_plot_path}")
    # plt.show()
# ---------------------------- Main Function ---------------------------- #

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

    # Define S-parameters to be processed
    s_parameters = {
        'S11': 'dB(St(1,1)) []',
        'S12': 'dB(St(1,2)) []',
        'S21': 'dB(St(2,1)) []',
        'S22': 'dB(St(2,2)) []'
    }

    # Create multi-line plots for consolidated data
    # create_multiline_plots(directory, s_parameters, plot_folder)

    # Consolidated data dictionary for summary and additional plots
    consolidated_data = {param: {} for param in s_parameters.keys()}

    # Create box plots for each S-parameter and material combination
    create_box_plots(consolidated_data, plot_folder, s_parameters)

    # Create radar plots for each S-parameter and material combination
    create_radar_plots(consolidated_data, plot_folder, s_parameters)

if __name__ == '__main__':
    main()