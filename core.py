from creation import new

file_path = r"C:\Users\hu3rt\Desktop\[Ln(2,2'-bpdo)4][Cr(CN)6]\EuCr_22bpdo_dT\Exc_spectra_T_map_30to300K_em614nm_0.5nm.txt"

thermap = new(file_path, 'test')
print(thermap.normalize(500.))



# test = pd.read_csv(file, skiprows=2)
#
# temps_row = test[test.iloc[:, 0] == 'Temp']
# print(test['Labels'])