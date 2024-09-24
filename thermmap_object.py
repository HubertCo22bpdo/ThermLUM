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
        return self.data

    def get_temperatures(self):
        self.temperatures = self.file[self.name][f'temperatures_{self.name}']
        return self.temperatures

    def normalize(self, normalization_value, save=False):
        initial_data = self.get_data()
        x_axis = initial_data[:, 0]
        normalization_row = None
        for index, value in enumerate(x_axis):
            if value == normalization_value:
                normalization_row = initial_data[index, 1:]
                break
        new_data = np.vstack((x_axis, (initial_data[:, 1:] / normalization_row).T)).T
        if save:
            try:
                self.file[self.name][f'data_{self.name}_normalized_to_{normalization_value}'] = new_data
            except Exception as e:
                print(e)
        return new_data



