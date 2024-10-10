# TherLUM - luminescent thermometry data analysis application
# Copyright (C) 2024  Hubert Dzielak 

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
import h5py
from os import path
from scipy.signal import savgol_filter

import numpy as np


class ThermMap:
    def __init__(self, hdf_file_path):
        self.file = h5py.File(hdf_file_path, 'r+')
        file_directory, file_name = path.split(hdf_file_path)
        self.name = file_name[:-5]
        self.directory = file_directory
        self.data = None
        self.temperatures = None

    def get_data(self):
        self.data = self.file[self.name][f'data_{self.name}'][...]
        self.x_data = self.data[:, 0].astype(np.float64)
        self.resolution = abs(self.data[-1, 0] - self.data[-2, 0])
        return self.data

    def get_temperatures(self):
        self.temperatures = self.file[self.name][f'temperatures_{self.name}'][...].astype(np.float64)
        return self.temperatures

    def get_row_of_ydata(self, x_value):
            if self.data is None:
                self.get_data()
            for index, value in enumerate(self.x_data):
                if value == x_value:
                    row = self.data[index, 1:]
                    return row
    
    @staticmethod
    def general_get_row_of_ydata(data, x_value):
            x_data = data[:, 0].astype(np.float64)
            for index, value in enumerate(x_data):
                if value == x_value:
                    row = data[index, 1:]
                    return row

    def normalize(self, normalization_value, save=False):
        normalization_row = self.get_row_of_ydata(normalization_value)
        normalized_data = np.vstack((self.x_data, (self.data[:, 1:] / normalization_row).T)).T
        if save:
            try:
                self.file[self.name][f'data_{self.name}_normalized_to_{normalization_value}'] = normalized_data
            except Exception as e:
                print(e)
        return normalized_data
            
    def smooth(self, window_length, polyorder, delta=1, save=False):
        if self.data is None:
            self.get_data()
        if self.temperatures is None:
            self.get_temperatures()
        smoothed_data = self.data.copy()
        for index, column in enumerate(smoothed_data[:, 1:].T):
            smoothed_data[:, index + 1] = savgol_filter(column, window_length=window_length, polyorder=polyorder, delta=delta, deriv=0)
        smooth_residual =  np.vstack((self.x_data, (smoothed_data[:, 1:] - self.data[:, 1:]).T)).T
        if save:
            try:
                self.file[self.name][f'data_{self.name}_smoothed'] = smoothed_data
                self.file[self.name][f'smooth_residuals_{self.name}'] = smooth_residual
            except Exception as e:
                print(e)
        return smoothed_data, smooth_residual
