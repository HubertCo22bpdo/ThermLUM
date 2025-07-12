# ThermLUM - luminescent thermometry data analysis application
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
from os import path, remove
from scipy.signal import savgol_filter
import numpy as np
import pandas as pd

def fluoracle_temerature_map_format(file_path):
    additional_data = {}
    file_directory, file_name = path.split(file_path)
    with open(file_path, "r") as file:
        lines_list = file.readlines()
    for index, line in enumerate(lines_list):
        if 'Labels' in line:
            start_description_index = index
        if 'Detector' in line:
            end_description_index = index

    description_contents = ''
    for line in lines_list[start_description_index:end_description_index + 1]:
        description_contents += line
    with open(path.join(file_directory, f'description_{file_name.split('.')[0]}'), 'w') as description_file:
        description_file.write(description_contents)

    description_df = pd.read_csv(description_file.name, sep=',')
    temps_row = description_df[description_df.iloc[:, 0] == 'Temp']
    temps = temps_row.iloc[:, 1:-1].to_numpy()[0]
    additional_data['Temperatures'] = f'Temperature range: {temps[0]}-{temps[-1]} K'
    start_row = description_df[description_df.iloc[:, 0] == 'Start']
    start = start_row.iloc[:, 1:-1].to_numpy()[0][0]
    stop_row = description_df[description_df.iloc[:, 0] == 'Stop']
    stop = stop_row.iloc[:, 1:-1].to_numpy()[0][0]
    additional_data['Wavelengths'] = f'Wavelengths range: {start}-{stop} nm'
    fixed_row = description_df[description_df.iloc[:, 0] == 'Fixed/Offset']
    fixed = fixed_row.iloc[:, 1:-1].to_numpy()[0][0]
    additional_data['Type Fixed Wavelength'] = f'{"Emission" if float(fixed) < float(start) else "Excitation"} scan for: {fixed} nm'
    repeats_row = description_df[description_df.iloc[:, 0] == 'Repeats']
    repeats = repeats_row.iloc[:, 1:-1].to_numpy()[0][0]
    additional_data['Repeats'] = f'Consecutive repeats of spectra: {repeats}'
    scan_slit_row = description_df[description_df.iloc[:, 0] == 'Scan Slit']
    scan_slit = scan_slit_row.iloc[:, 1:-1].to_numpy()[0][0]
    fixed_slit_row = description_df[description_df.iloc[:, 0] == 'Fixed/Offset Slit']
    fixed_slit = fixed_slit_row.iloc[:, 1:-1].to_numpy()[0][0]
    additional_data['Slits'] = f'Slit settings: Scan {scan_slit} nm, Fixed {fixed_slit}'
    dwell_row = description_df[description_df.iloc[:, 0] == 'Dwell Time']
    dwell = dwell_row.iloc[:, 1:-1].to_numpy()[0][0]
    additional_data['Dwell Time'] = f'Dwell Time: Scan {dwell} s'
    additional_data['File Name'] = file_name

    data_contents = ''
    for line in lines_list[end_description_index + 1:]:
        data_contents += line
    with open(path.join(file_directory, f'_temp_data_{file_name.split('.')[0]}.csv'), 'w') as data_file:
        data_file.write(data_contents)

    data_df = pd.read_csv(data_file.name, sep=',', header=None)
    data_df = data_df.iloc[:, :-1] # index -1 removes nan column previously containing new line symbols

    if path.exists(path.join(file_directory, f'description_{file_name.split('.')[0]}')): 
        remove(path.join(file_directory, f'description_{file_name.split('.')[0]}'))
    if path.exists(path.join(file_directory, f'_temp_data_{file_name.split('.')[0]}.csv')): 
        remove(path.join(file_directory, f'_temp_data_{file_name.split('.')[0]}.csv'))

    return data_df, temps, additional_data

class ThermMap:
    def __init__(self, hdf_file_path):
        self.file = h5py.File(hdf_file_path, 'r+')
        file_directory, file_name = path.split(hdf_file_path)
        self.name = file_name[:-5]
        self.directory = file_directory
        self.data = None
        self.temperatures = None
        self.repeatability_indexes = []

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
    
    @staticmethod
    def limit_temperature_range(data_df, temps, additional_data, lower_lim=None, upper_lim=None, list_of_lim=[]):
        surviving_temps_indexes = []
        new_temps = []
        for pos, temperature in enumerate(temps):
            temperature = float(temperature)
            if lower_lim is not None:
                if lower_lim > temperature:
                    continue
            if upper_lim is not None:
                if upper_lim < temperature:
                    continue
            if round(temperature, 5) in list_of_lim:
                continue
            surviving_temps_indexes.append(pos+1) #To account for first column being Wavelengths
            new_temps.append(temperature)
        data_df = data_df.iloc[:, [0]+surviving_temps_indexes]
        additional_data['Dropped temperatures'] = list(set(temps) - set(new_temps))
        return data_df, new_temps, additional_data
    
    @staticmethod
    def find_next_index(list):
        n = 0
        while True:
            if n not in list:
                return n
            else:
                n += 1
    
    def add_repeatability_data(self, data_df, temps, additional_data):
        index = self.find_next_index(self.repeatability_indexes)

        if 'Repeatability' in self.file[self.name].keys():
            rep_group = self.file[self.name]['Repeatability']
        else:
            rep_group = self.file[self.name].create_group('Repeatability')
        rep_group.create_dataset(f'rep_data_{index}', data=data_df)
        rep_group.create_dataset(f'rep_temperatures_{index}', data=temps)
        for key, value in additional_data.items():
            rep_group[f'rep_data_{index}'].attrs[key] = value
        rep_group[f'rep_data_{index}'].attrs['Repeatability Index'] = index 
        self.repeatability_indexes.append(index)

        return index

    def remove_repeatability_data(self, index):
        # To account for weird behaviour of 
        try:
            self.repeatability_indexes.remove(index)
            del self.file[self.name]['Repeatability'][f'rep_data_{index}']
            del self.file[self.name]['Repeatability'][f'rep_temperatures_{index}']
        except:
            print('TherMap.remove_repeatability anomaly, if only symptom is this message - ignore')
            pass

    def repeatability(self, list_of_indexes, parameter_numerator, parameter_denominator, intensity=None):
        all_cycles_data = []
        if len(list_of_indexes) > 1:
            if type(list_of_indexes[1]) == list:
                self.remove_repeatability_data(list_of_indexes[0])
                list_of_indexes = list_of_indexes[1]
        for index in list_of_indexes:
            rep_data = self.file[self.name]['Repeatability'][f'rep_data_{index}'][...]
            if intensity is None:
                all_cycles_data.append((self.general_get_row_of_ydata(rep_data, parameter_numerator) / self.general_get_row_of_ydata(rep_data, parameter_denominator))[...])
            elif intensity == 'N':
                all_cycles_data.append(self.general_get_row_of_ydata(rep_data, parameter_numerator)[...])
            elif intensity == 'D':
                all_cycles_data.append(self.general_get_row_of_ydata(rep_data, parameter_denominator)[...])

        return all_cycles_data