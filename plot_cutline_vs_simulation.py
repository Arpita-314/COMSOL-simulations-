import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import h5py
import argparse
import math


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
            x_axis = np.arange(B.shape[1])
            plt.plot(x_axis, B[20:30, :].mean(axis=0) * conversion_factor, label=key)
        plt.title('Averaged Data Cutlines Comparison')
        plt.xlabel('Pixel Position')
        plt.ylabel('uT')
        plt.legend()
        plt.show()

# Step 3: Rotate the "Averaged Cutline" data
def rotate_data(x, y, angle):
    rotation_matrix = np.array([
        [np.cos(angle), -np.sin(angle)],
        [np.sin(angle), np.cos(angle)]
    ])
    data = np.vstack((x, y))
    rotated_data = rotation_matrix @ data
    return rotated_data[0], rotated_data[1]


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

        model = LinearRegression()
        model.fit(x, y)
        y_pred = model.predict(x)

        print(f"File: {file_path}")
        print("Slope (m):", model.coef_[0])
        print("Intercept (b):", model.intercept_)

        plt.figure(dpi=400)
        
        plt.scatter((x+1.25e-5)*10e5, y, label='Gradient magnetic field (G/um)', marker='.', color='blue')
        plt.plot((x+1.25e-5)*10e5, y_pred, label='Fitted data', color='red')
        x_fitted = (x+1.25e-5)*10e5
        y_fitted = y_pred
        for key, B in averaged_cutline_data.items():
            x_axis = np.arange(B.shape[1])
            
        y_axis =  B[20:30, :].mean(axis=0) * conversion_factor
        plt.plot(x_axis, y_axis, label=f'Averaged Cutline {key}')

        # Step 1: Fit a line to the "Averaged Cutline"
        x_cutline_reshaped = x_axis.reshape(-1, 1)
        reg_cutline = LinearRegression().fit(x_cutline_reshaped, y_axis)
        slope_cutline = reg_cutline.coef_[0]

        # Fit a line to the "Fitted Data"
        x_fitted_reshaped = x_fitted.reshape(-1, 1)
        reg_fitted = LinearRegression().fit(x_fitted_reshaped, y_fitted)
        slope_fitted = reg_fitted.coef_[0]

        # Step 2: Calculate the angle between the two lines
        angle = math.atan(slope_cutline) - math.atan(slope_fitted)

        x_rotated, y_rotated = rotate_data(x_axis, y_axis, -angle)

        # Step 4: Plot the original and aligned data
        plt.figure(figsize=(10, 6), dpi=400)

        # Original data
        # plt.plot(x_axis, y_axis, 'b-', label='Original Averaged Cutline')
        # plt.plot(x_fitted, y_fitted, 'r-', label='Fitted Data')

        # Rotated data
        plt.scatter(x_fitted+25, y, label='Gradient magnetic field (G/um)', marker='.', color='blue')
        plt.plot(x_fitted+25, y_fitted, label='Fitted data', color='red')
        plt.plot(x_rotated, y_rotated, 'g', label=' Averaged Cutline')

        plt.xlabel('um')
        plt.ylabel('Gradient Magnetic field (G)')
        plt.legend()
        # plt.title(f'Gradient magnetic field vs spatial resolution - {current_density} G/um')
        plt.show()

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot cutline vs simulation.')
    parser.add_argument('file_path', type=str, help='Path to the .txt file for plotting')
    args = parser.parse_args()

    base_measurement_folder = r'/home/sparks/Documents/h5_files_storage'

    filenames_average_cutlines = {
        '20241030_40mA': {
            'background_right': '20241030_10-47_ODMR_fitted_bg',
            'background_left': '20241030_11-15_ODMR_fitted_bg',
            'signal_right': '20241030_12-50_ODMR_fitted_r40mA',
            'signal_left': '20241030_12-16_ODMR_fitted_l40mA'
        }
    }

    average_cutline_processing = AverageCutlineProcessing(base_measurement_folder, filenames_average_cutlines)
    average_cutline_processing.remove_background_signal()

    plot_data(args.file_path, conversion_factor=0.6896551724137931, averaged_cutline_data=average_cutline_processing.B)