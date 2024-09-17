import h5py
from os import path


class ThermMap:
    def __init__(self, hdf_file_path):
        self.file = h5py.File(hdf_file_path, 'r+')
        file_directory, file_name = path.split(hdf_file_path)
        self.name = file_name[:-5]
        self.directory = file_directory

    def get_data(self):
        return self.file[self.name][f'data_{self.name}']

    def get_temperatures(self):
        return self.file[self.name][f'temperatures_{self.name}']
