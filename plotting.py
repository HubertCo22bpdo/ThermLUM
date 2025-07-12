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
import matplotlib.pyplot as plt
import numpy as np
#EGG

def luminescence_dt(data, temperatures, axes: plt.Axes, colormap):
    counter = 0
    for temperature in temperatures:
        axes.plot(data[:, 0], data[:, 1+counter], label=f'{temperature} K', color=colormap(counter), picker=False, linewidth=0.75)
        axes.set_xlabel('Wavelength / nm')
        axes.set_ylabel('Intensity')
        counter += 1

    return axes

def reproducibility_cycles(data, axes: plt.Axes, color, return_list_of_values=False):
    list_of_values = []
    # number_of_points = 0
    for dataset in data:
        list_of_values.extend(dataset)
        # number_of_points += len(dataset)
    axes.plot(list_of_values, color=color, marker='o', mfc='none', ls='-')
    axes.set_xlabel('Cycles')
    axes.set_ylabel('Thermometric parameter')

    if return_list_of_values:
        return (list_of_values, axes)
    else:
        return axes

def draw_std(axes, temp_mean_std_data_dict, colormap):
    for pos, temperature in enumerate(sorted(temp_mean_std_data_dict.keys(), key=lambda dkey: float(dkey))):
        mean = temp_mean_std_data_dict[temperature][1]
        std = temp_mean_std_data_dict[temperature][2]
        N = len(temp_mean_std_data_dict.keys())
        axes.axhspan(mean-std, mean+std, color=colormap(((pos+1)/N)), alpha=0.3)
        axes.axhline(mean, ls='--', color=colormap(((pos+1)/N)))
        
    return axes
