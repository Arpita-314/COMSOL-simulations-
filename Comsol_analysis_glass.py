import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Set the directory containing the files and create a folder for plots
data_folder = 'H:\\Comsol simulations\\glass slides'  # Replace with your folder path
plot_folder = os.path.join(data_folder, "plots")
os.makedirs(plot_folder, exist_ok=True)

# Initialize lists to store data for positive and negative currents
positive_data = []
negative_data = []

# Loop through all files in the directory
for file_name in os.listdir(data_folder):
    if file_name.endswith('.txt'):  # Process only .txt files
        file_path = os.path.join(data_folder, file_name)
        
        try:
            # Load data from the file and handle the header
            print(f"Loading file: {file_name}")
            data = np.loadtxt(file_path, skiprows=8)  # Skip the first 8 rows of header information
            
            if data.size == 0:
                print(f"Warning: File {file_name} seems to be empty after skipping rows. Skipping...")
                continue

            # Extract x and y
            x = data[:, 0].reshape(-1)  # Column 1 is X
            y = data[:, 2]  # Column 2 is Y
            
            # Check if x or y are empty
            if len(x) == 0 or len(y) == 0:
                print(f"Warning: No data available in file {file_name}. Skipping...")
                continue
            
            # Extract current density value from the filename for labeling purposes
            current_density = file_name.replace('.txt', '')
            
            # Separate data based on whether filename indicates positive or negative current
            if current_density.startswith('-'):
                negative_data.append((x, y, current_density))
            else:
                positive_data.append((x, y, current_density))
            
            # Create and fit a polynomial model (degree 3)
            poly_coefficients = np.polyfit(x, y, 3)
            y_pred = np.polyval(poly_coefficients, x)
            
            # Print polynomial coefficients
            print(f"File: {file_name}")
            print("Polynomial Coefficients (degree 3):", poly_coefficients)
            
            # Plot the original data and the polynomial fit
            plt.figure(dpi=400)  # Set the DPI to 400 for high resolution
            plt.scatter(x, y, label='Gradient magnetic field (G/um)', marker='.', color='blue')
            plt.plot(x, y_pred, label='Polynomial Fit (Degree 3)', color='red')
            plt.xlabel('um')
            plt.ylabel('Gradient Magnetic field (G)')
            plt.legend()
            plt.title(f'Gradient magnetic field vs spatial resolution - {current_density} G/um')
            plt.savefig(os.path.join(plot_folder, f"{file_name.split('.')[0]}_plot.png"))
            
            print(f"Plot saved: {file_name.split('.')[0]}_plot.png\n")
            
        except Exception as e:
            print(f"Error processing file {file_name}: {e}")
            continue

# %% Plot combined data for positive currents with polynomial fit
if len(positive_data) > 0:
    plt.figure(figsize=(12, 8), dpi=400)  # Set the DPI to 400 for high resolution
    
    # Combine all positive current data into single arrays
    all_x_positive = np.concatenate([x for x, _, _ in positive_data])
    all_y_positive = np.concatenate([y for _, y, _ in positive_data])
    
    # Plot individual data points
    for x, y, current_density in positive_data:
        plt.scatter(x, y, label=f'{current_density} G/um', alpha=0.7)

    # Perform a polynomial fit (3rd degree) for the combined data
    # poly_coefficients_positive = np.polyfit(all_x_positive, all_y_positive, 3)
    # y_pred_positive = np.polyval(poly_coefficients_positive, all_x_positive)
    
    # Plot the fitted polynomial for combined data
    # plt.plot(all_x_positive, y_pred_positive, color='red', label='Combined Polynomial Fit (Degree 3)', linewidth=2)
    
    # Labels and legend
    plt.xlabel('um')
    plt.ylabel('Gradient Magnetic field (G)')
    # plt.title()
    plt.legend(loc='upper right')
    positive_plot_path = os.path.join(plot_folder, "combined_positive_plot_with_fit.png")
    plt.savefig(positive_plot_path)
    plt.close()
    print(f"Combined plot for positive current with polynomial fit saved: {positive_plot_path}\n")
else:
    print("No data available for positive currents.")

# %% Plot combined data for negative currents with polynomial fit
if len(negative_data) > 0:
    plt.figure(figsize=(12, 8), dpi=400)  # Set the DPI to 400 for high resolution
    
    # Combine all negative current data into single arrays
    all_x_negative = np.concatenate([x for x, _, _ in negative_data])
    all_y_negative = np.concatenate([y for _, y, _ in negative_data])
    
    # Plot individual data points
    for x, y, current_density in negative_data:
        plt.scatter(x, y, label=f'{current_density} G/um', alpha=0.7)

    # Perform a polynomial fit (3rd degree) for the combined data
    # poly_coefficients_negative = np.polyfit(all_x_negative, all_y_negative, 3)
    # y_pred_negative = np.polyval(poly_coefficients_negative, all_x_negative)
    
    # # Plot the fitted polynomial for combined data
    # plt.plot(all_x_negative, y_pred_negative, color='red', label='Combined Polynomial Fit (Degree 3)', linewidth=2)
    
    # Labels and legend
    plt.xlabel('um')
    plt.ylabel('Gradient Magnetic field (G)')
    # plt.title()
    plt.legend(loc='lower right')
    negative_plot_path = os.path.join(plot_folder, "combined_negative_plot_with_fit.png")
    plt.savefig(negative_plot_path)
    plt.close()
    print(f"Combined plot for negative current with polynomial fit saved: {negative_plot_path}\n")
else:
    print("No data available for negative currents.")
