import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from math import pi
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

            # Identify the x-axis column
            x_column = None
            for col in data.columns:
                if 'freq' in col.lower():
                    x_column = col
                    break

            if x_column is None:
                # If no frequency column is found, use the first column as x-axis
                x_column = data.columns[0]
                print(f"No frequency column found in '{csv_path}'. Using '{x_column}' as x-axis.")

            # Check if x_column is numeric
            if not np.issubdtype(data[x_column].dtype, np.number):
                print(f"Error: The x-axis column '{x_column}' in '{csv_path}' is not numeric. Skipping.")
                continue

            # Use the remaining columns as y-axis
            y_columns = [col for col in data.columns if col != x_column]

            if not y_columns:
                print(f"No data columns found for plotting in '{csv_path}'.")
                continue

            # Determine the directory of the CSV file and create a plot folder inside the CSV file's directory
            csv_dir = os.path.dirname(csv_path)
            subfolder_name = os.path.basename(csv_dir)
            plot_folder_name = f"{subfolder_name} plot"
            sub_plot_folder = os.path.join(csv_dir, plot_folder_name)
            os.makedirs(sub_plot_folder, exist_ok=True)

            # Store data for plotting (using the first y-column as per requirement)
            frequency = data[x_column]  # Frequency in GHz
            for y_column in y_columns:
                if 's11' in y_column.lower():
                    s11 = data[y_column]  # S11 parameter in dB
                    material_data.append((frequency, s11, subfolder_name, 'S11'))
                    # Store data for consolidated plot
                    height = subfolder_name.split('nm')[0].strip()  # Extract height from folder name
                    if height.isdigit():
                        height = int(height)
                        if subfolder_name not in consolidated_data['S11']:
                            consolidated_data['S11'][subfolder_name] = {}
                        consolidated_data['S11'][subfolder_name][height] = s11
                elif 's12' in y_column.lower():
                    s12 = data[y_column]  # S12 parameter in dB
                    material_data.append((frequency, s12, subfolder_name, 'S12'))
                    if height.isdigit():
                        if subfolder_name not in consolidated_data['S12']:
                            consolidated_data['S12'][subfolder_name] = {}
                        consolidated_data['S12'][subfolder_name][height] = s12
                elif 's21' in y_column.lower():
                    s21 = data[y_column]  # S21 parameter in dB
                    material_data.append((frequency, s21, subfolder_name, 'S21'))
                    if height.isdigit():
                        if subfolder_name not in consolidated_data['S21']:
                            consolidated_data['S21'][subfolder_name] = {}
                        consolidated_data['S21'][subfolder_name][height] = s21
                elif 's22' in y_column.lower():
                    s22 = data[y_column]  # S22 parameter in dB
                    material_data.append((frequency, s22, subfolder_name, 'S22'))
                    if height.isdigit():
                        if subfolder_name not in consolidated_data['S22']:
                            consolidated_data['S22'][subfolder_name] = {}
                        consolidated_data['S22'][subfolder_name][height] = s22
                elif 'z11' in y_column.lower():
                    z11 = data[y_column]  # Z11 parameter
                    material_data.append((frequency, z11, subfolder_name, 'Z11'))
                    if height.isdigit():
                        if subfolder_name not in consolidated_data['Z11']:
                            consolidated_data['Z11'][subfolder_name] = {}
                        consolidated_data['Z11'][subfolder_name][height] = z11
                elif 'z12' in y_column.lower():
                    z12 = data[y_column]  # Z12 parameter
                    material_data.append((frequency, z12, subfolder_name, 'Z12'))
                    if height.isdigit():
                        if subfolder_name not in consolidated_data['Z12']:
                            consolidated_data['Z12'][subfolder_name] = {}
                        consolidated_data['Z12'][subfolder_name][height] = z12
                elif 'z21' in y_column.lower():
                    z21 = data[y_column]  # Z21 parameter
                    material_data.append((frequency, z21, subfolder_name, 'Z21'))
                    if height.isdigit():
                        if subfolder_name not in consolidated_data['Z21']:
                            consolidated_data['Z21'][subfolder_name] = {}
                        consolidated_data['Z21'][subfolder_name][height] = z21
                elif 'z22' in y_column.lower():
                    z22 = data[y_column]  # Z22 parameter
                    material_data.append((frequency, z22, subfolder_name, 'Z22'))
                    if height.isdigit():
                        if subfolder_name not in consolidated_data['Z22']:
                            consolidated_data['Z22'][subfolder_name] = {}
                        consolidated_data['Z22'][subfolder_name][height] = z22
                elif 'tdr-impedance' in y_column.lower():
                    tdr_impedance = data[y_column]  # TDR-Impedance parameter
                    material_data.append((frequency, tdr_impedance, subfolder_name, 'TDR-Impedance'))
                    if height.isdigit():
                        if subfolder_name not in consolidated_data['TDR-Impedance']:
                            consolidated_data['TDR-Impedance'][subfolder_name] = {}
                        consolidated_data['TDR-Impedance'][subfolder_name][height] = tdr_impedance
                elif 'z0' in y_column.lower():
                    z0 = data[y_column]  # Z0 parameter
                    material_data.append((frequency, z0, subfolder_name, 'Z0'))
                    if height.isdigit():
                        if subfolder_name not in consolidated_data['Z0']:
                            consolidated_data['Z0'][subfolder_name] = {}
                        consolidated_data['Z0'][subfolder_name][height] = z0

        except pd.errors.EmptyDataError:
            print(f"Warning: The file '{csv_path}' is empty or contains only headers. Skipping.")
        except pd.errors.ParserError as e:
            print(f"Error parsing '{csv_path}': {e}. Skipping.")
        except Exception as e:
            print(f"Error processing '{csv_path}': {e}. Skipping.")

    # Plot S11, S12, S21, S22 parameter against frequency for different materials
    for param in ['S11', 'S12', 'S21', 'S22']:
        plt.figure(figsize=(10, 6), dpi=400)  # Set the DPI to 400 for high resolution

        # Iterate through the collected data and plot
        for frequency, s_param, material, param_type in material_data:
            if param_type == param:
                plt.plot(frequency, s_param, label=f'{material}')

        # Labels and legend
        plt.xlabel('Frequency (GHz)')
        plt.ylabel(f'{param} Parameter (dB)')
        plt.title(f'Impedance Match ({param}) vs Frequency for Different Materials')
        plt.legend(loc='upper right')

        # Save the combined plot
        combined_plot_path = os.path.join(plot_folder, f"impedance_match_vs_frequency_{param}.png")
        plt.savefig(combined_plot_path)
        plt.show()
        plt.close()
        print(f"Combined {param} impedance match plot saved: {combined_plot_path}")

        # Create a DataFrame to summarize results
        summary_data = []
        for frequency, s_param, material, param_type in material_data:
            if param_type == param:
                max_value = s_param.max()
                min_value = s_param.min()
                summary_data.append([material, max_value, min_value])

        summary_df = pd.DataFrame(summary_data, columns=['Material', 'Max Value (dB)', 'Min Value (dB)'])
        summary_path = os.path.join(plot_folder, f"summary_{param}_impedance_match.csv")
        summary_df.to_csv(summary_path, index=False)
        print(f"Summary table for {param} saved: {summary_path}")

    # Box plot for S11 Min/Max Values Across All Metals
    plt.figure(figsize=(10, 6), dpi=400)
    s11_min_values = [data[2] for data in summary_data if data[0] == 'S11']
    s11_max_values = [data[1] for data in summary_data if data[0] == 'S11']
    plt.boxplot([s11_min_values, s11_max_values], labels=['Min Values', 'Max Values'])
    plt.xlabel('S11 Metrics')
    plt.ylabel('S11 Value (dB)')
    plt.title('Box Plot of S11 Min and Max Values for All Metal Combinations')
    plt.savefig(os.path.join(plot_folder, 'boxplot_s11_min_max.png'))
    plt.show()
    plt.close()

    # Bar Chart for Average S11 Values for Each Metal Combination
    avg_s11_values = []
    materials = []
    for material, height_data in consolidated_data['S11'].items():
        avg_value = np.mean([data.mean() if isinstance(data, pd.Series) else 0 for height, data in height_data.items()])
        avg_s11_values.append(avg_value)
        materials.append(material)

    plt.figure(figsize=(10, 6), dpi=400)
    plt.bar(materials, avg_s11_values, color='skyblue')
    plt.xlabel('Material')
    plt.ylabel('Average S11 Value (dB)')
    plt.title('Average S11 Values for Each Metal Combination')
    plt.xticks(rotation=45)
    plt.savefig(os.path.join(plot_folder, 'bar_chart_avg_s11.png'))
    plt.show()
    plt.close()

    # Radar Plot for Overall Comparison of Different Metrics
    

    radar_data = {}
    params = ['S11', 'S12', 'S21', 'S22', 'Z0', 'TDR-Impedance']
    for param in params:
        for material, height_data in consolidated_data[param].items():
            avg_value = np.mean([data.mean() for height, data in height_data.items()])
            if material not in radar_data:
                radar_data[material] = []
            radar_data[material].append(avg_value)

    labels = params
    num_vars = len(labels)

    for material, values in radar_data.items():
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        values += values[:1]
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax.fill(angles, values, color='skyblue', alpha=0.25)
        ax.plot(angles, values, color='skyblue', linewidth=2)
        ax.set_yticklabels([])
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels)
        plt.title(f'Radar Plot for {material}')
        radar_plot_path = os.path.join(plot_folder, f'radar_plot_{material}.png')
        plt.savefig(radar_plot_path)
        plt.show()
        plt.close()

    # Heatmap for S11 vs Height vs Frequency
    heatmap_data = []
    for material, height_data in consolidated_data['S11'].items():
        heights = sorted(height_data.keys())
        if len(frequency_data) > 0:
          frequency_concat = pd.concat(frequency_data, axis=1).fillna(0).values
        else:
          print(f"Warning: No data available for heatmap generation for {material}. Skipping...")
        continue
        frequency_data = [height_data[height] for height in heights]
        frequency_concat = pd.concat(frequency_data, axis=1).values
        heatmap_data.append((heights, frequency_concat))

        plt.figure(figsize=(12, 6), dpi=400)
        plt.imshow(frequency_concat, aspect='auto', cmap='viridis', interpolation='none')
        plt.colorbar(label='S11 Value (dB)')
        plt.xlabel('Frequency (Index)')
        plt.ylabel('Height (nm)')
        plt.title(f'Heatmap of S11 vs Height vs Frequency for {material}')
        heatmap_path = os.path.join(plot_folder, f'heatmap_s11_{material}.png')
        plt.savefig(heatmap_path)
        plt.show()
        plt.close()

if __name__ == '__main__':
    main()
