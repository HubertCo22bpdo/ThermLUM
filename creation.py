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
import pandas as pd
import h5py
import numpy as np
from os import path
def new(file_path, hdf_name):
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

    data_contents = ''
    for line in lines_list[end_description_index + 1:]:
        data_contents += line
    with open(path.join(file_directory, f'_temp_data)_{file_name.split('.')[0]}.csv'), 'w') as data_file:
        data_file.write(data_contents)

    data_df = pd.read_csv(data_file.name, sep=',', header=None)
    data_df = data_df.iloc[:, :-1] # index -1 removes nan column previously containing new line symbols

    hdf_file_path = path.join(file_directory, hdf_name+'.hdf5')
    hdf_file = h5py.File(hdf_file_path, 'w')
    group = hdf_file.create_group(hdf_name)
    group.create_dataset(f'data_{hdf_name}', data=data_df)
    group.create_dataset(f'temperatures_{hdf_name}', data=temps)
    hdf_file.close()

    from thermmap_object import ThermMap
    return ThermMap(hdf_file_path)
