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
