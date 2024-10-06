# from creation import new

# file_path = r"C:\Users\hu3rt\Desktop\[Ln(2,2'-bpdo)4][Cr(CN)6]\EuCr_22bpdo_dT\Exc_spectra_T_map_30to300K_em614nm_0.5nm.txt"

# thermap = new(file_path, 'test')
# print(thermap.normalize(500.))



# test = pd.read_csv(file, skiprows=2)
#
# temps_row = test[test.iloc[:, 0] == 'Temp']
# print(test['Labels'])

from scipy.signal import savgol_filter
import numpy as np

# Generate some noisy data
x = np.linspace(0, 10, 100)
y = np.sin(x) + np.random.normal(0, 0.1, 100)

# Apply Savitzky-Golay filter with window size 5 and polynomial order 2
y_filtered = savgol_filter(y, window_length=5, polyorder=2, delta=0.1)

# Plot original and filtered data
import matplotlib.pyplot as plt

plt.plot(x, y, label='Noisy Data')
plt.plot(x, y_filtered, label='Filtered Data')
plt.legend()
plt.show()