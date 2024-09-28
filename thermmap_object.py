import h5py
from os import path

import numpy as np


class ThermMap:
    def __init__(self, hdf_file_path):
        self.file = h5py.File(hdf_file_path, 'r+')
        file_directory, file_name = path.split(hdf_file_path)
        self.name = file_name[:-5]
        self.directory = file_directory

    def get_data(self):
        self.data = self.file[self.name][f'data_{self.name}']
        self.x_data = self.data[:, 0].astype(np.float64)
        return self.data

    def get_temperatures(self):
        self.temperatures = self.file[self.name][f'temperatures_{self.name}'][...].astype(np.float64)
        return self.temperatures

    def normalize(self, normalization_value, save=False):
        normalization_row = self.get_row_of_ydata(normalization_value)
        new_data = np.vstack((self.x_data, (self.data[:, 1:] / normalization_row).T)).T
        if save:
            try:
                self.file[self.name][f'data_{self.name}_normalized_to_{normalization_value}'] = new_data
            except Exception as e:
                print(e)
        return new_data

    def get_row_of_ydata(self, x_value):
        self.get_data()
        for index, value in enumerate(self.x_data):
            if value == x_value:
                row = self.data[index, 1:]
                return row
