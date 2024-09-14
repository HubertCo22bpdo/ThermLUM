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
    print(description_df)

    data_contents = ''
    for line in lines_list[end_description_index + 1:]:
        data_contents += line
    with open(path.join(file_directory, f'_temp_data)_{file_name.split('.')[0]}.csv'), 'w') as data_file:
        data_file.write(data_contents)

    data_df = pd.read_csv(data_file.name, sep=',', header=None)
    print(data_df.dropna(axis=1, how='any'))


