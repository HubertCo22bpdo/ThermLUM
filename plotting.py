import matplotlib.pyplot as plt
import numpy as np


def luminescence_dt(data, temperatures, axes:plt.Axes, colormap):
    counter = 0
    for temperature in temperatures:
        axes.plot(data[:, 0], data[:, 1+counter], label=f'{temperature} K', color=colormap(counter))
        counter += 1

    return axes
