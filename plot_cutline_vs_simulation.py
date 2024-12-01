# -- coding: utf-8 --
"""
Created on Sun Dec  1 19:07:24 2024

@author: go29lap
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import h5py
import argparse


class AverageCutlineProcessing:
    def __init__(self, base_measurement_folder, filenames):
        self.base_measurement_folder = base_measurement_folder
        self.filenames = filenames
        self.data_background = {}
        self.data_signal = {}
        self.B = {}

    def load_data(self, name):
        measurement_folder = os.path.join(self.base_measurement_folder, name)
        file_path = os.path.join(measurement_folder, f'{name}.hdf5')

        try:
            with h5py.File(file_path, 'r') as f:
                data = np.array(f['data']['fit_param'])
            return data
        except Exception as e:
            print(f"Error opening {file_path}: {e}")
            return None

    def remove_background_signal(self):
        for key, files in self.filenames.items():
            data_bg_right = self.load_data(files['background_right'])
            data_bg_left = self.load_data(files['background_left'])
            data_signal_right = self.load_data(files['signal_right'])
            data_signal_left = self.load_data(files['signal_left'])

            if data_bg_right is None or data_bg_left is None or data_signal_left is None or data_signal_right is None:
                print(f"One or more data files could not be loaded for {key}.")
                continue

            self.data_background[key] = data_bg_right - data_bg_left
            self.data_signal[key] = data_signal_right - data_signal_left
            self.B[key] = (self.data_signal[key] - self.data_background[key]) / 28e3

    def plot_averaged_cutlines(self, conversion_factor):
        plt.figure(figsize=(10, 5))
        for key, B in self.B.items():
            x_axis = np.arange(B.shape[1]) * conversion_factor  # Convert x-axis from pixels to µm
            plt.plot(x_axis, B[20:30, :].mean(axis=0), label=key)
        plt.title('Averaged Data Cutlines Comparison')
        plt.xlabel('Position (µm)')
        plt.ylabel('uT')
        plt.legend()
        plt.show()

def plot_data(file_path, conversion_factor, averaged_cutline_data):
    try:
        print(f"Loading file: {file_path}")
        data = np.loadtxt(file_path, skiprows=1)

        if data.size == 0:
            print(f"Warning: File {file_path} seems to be empty after skipping rows. Skipping...")
            return

        x = data[:, 0].reshape(-1, 1)
        y = data[:, 2]

        if len(x) == 0 or len(y) == 0:
            print(f"Warning: No data available in file {file_path}. Skipping...")
            return

        current_density = os.path.basename(file_path).replace('.txt', '')

        # Convert x-axis from pixels to micrometers and center around 0
        x_um = (x - x.mean()) * conversion_factor
        x_um_range = np.linspace(-15, 15, len(x_um))  # Adjust the range to match simulation data

        # Linear regression for experimental data
        model_exp = LinearRegression()
        model_exp.fit(x_um, y)
        y_pred_exp = model_exp.predict(x_um)

        print(f"File: {file_path}")
        print("Experimental Data Slope (m):", model_exp.coef_[0])
        print("Experimental Data Intercept (b):", model_exp.intercept_)

        # Define endpoints for simulated data and create linear fit
        x_sim_points = np.array([[-15], [15]])
        y_sim_points = np.array([37, -37])

        # Linear regression for simulated data
        model_sim = LinearRegression()
        model_sim.fit(x_sim_points, y_sim_points)
        y_pred_sim = model_sim.predict(x_sim_points)

        print("Simulated Data Slope (m):", model_sim.coef_[0])
        print("Simulated Data Intercept (b):", model_sim.intercept_)

        # Plotting
        plt.figure(dpi=400)
        # Scatter plot for experimental data
        # plt.scatter(x_um_range, y, label='Experimental Data (Gradient magnetic field G/um)', marker='.', color='blue')
        # plt.plot(x_um_range, y_pred_exp, label='Fitted Experimental Data', color='red')

        # Scatter plot for simulated endpoints and linear fit
        additional_points_x = np.array([[-10], [-5], [0], [5], [10]])
        additional_points_y = model_sim.predict(additional_points_x)
        # x_sim_points = np.concatenate((x_sim_points, additional_points_x))
        # y_sim_points = np.concatenate((y_sim_points, additional_points_y))
        plt.scatter(additional_points_x, additional_points_y, color='purple', marker = '.')
        plt.scatter(x_sim_points, y_sim_points, color='purple', marker = '.', label='Simulated Data Points')
        plt.plot(x_sim_points, y_pred_sim, color='orange', label='Fitted Simulated Data')

        # Plot averaged cutline data from simulation
        for key, B in averaged_cutline_data.items():
            x_axis_simulation = np.linspace(-15, 15, B.shape[1])
            averaged_data = B[20:30, :].mean(axis=0) * conversion_factor

            if len(x_axis_simulation) == len(averaged_data):  # Ensure x and y have the same length
                plt.plot(x_axis_simulation, averaged_data, label=f'Averaged Cutline {key}')
            else:
                print(f"Warning: Mismatch in data length for {key}, skipping plotting this cutline.")

        plt.xlabel('Spatial Position (µm)')
        plt.ylabel('Gradient Magnetic Field (G)')
        plt.legend()
        plt.title(f'Gradient magnetic field vs spatial resolution - {current_density} G/um')
        plt.show()

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot cutline vs simulation.')
    parser.add_argument('file_path', type=str, help='Path to the .txt file for plotting')
    args = argparse.Namespace(file_path=r'/home/sparks/Documents/diamond/1e10.txt')

    base_measurement_folder = r'/home/sparks/Documents/'

    filenames_average_cutlines = {
        '20241030_40mA': {
            'background_right': '20241030_10-47_ODMR_fitted_bg',
            'background_left': '20241030_11-15_ODMR_fitted_bg',
            'signal_right': '20241030_21-55_ODMR_fitted_ro40mA',
            'signal_left': '20241030_21-27_ODMR_fitted_lo40mA'
        }
    }

    average_cutline_processing = AverageCutlineProcessing(base_measurement_folder, filenames_average_cutlines)
    average_cutline_processing.remove_background_signal()

    plot_data(args.file_path, conversion_factor=0.6896551724137931, averaged_cutline_data=average_cutline_processing.B)