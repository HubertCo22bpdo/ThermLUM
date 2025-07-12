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
from os import path
from thermmap_object import fluoracle_temerature_map_format



def new(file_path, hdf_name, format='fluoracle_themerature_map'):
    file_directory, file_name = path.split(file_path)

    if format == 'fluoracle_themerature_map':
        data_df, temps, additional_data = fluoracle_temerature_map_format(file_path)
    
    hdf_file_path = path.join(file_directory, hdf_name+'.hdf5')
    hdf_file = h5py.File(hdf_file_path, 'w')
    group = hdf_file.create_group(hdf_name)
    data_dataset = group.create_dataset(f'data_{hdf_name}', data=data_df)
    for key, value in additional_data.items():
            data_dataset.attrs[key] = value
    group.create_dataset(f'temperatures_{hdf_name}', data=temps)
    hdf_file.close()

    

    from thermmap_object import ThermMap
    return ThermMap(hdf_file_path)
