import pickle
import os

# read file names in delitos folder
files = os.listdir('delitos')
delitos_completos = set()
for file in files:
    # separate file name and extension
    file_name, file_extension = os.path.splitext(file)
    # split file name by _
    file_name = file_name.split('_')
    # add to set
    comuna = file_name[0]
    año = int(file_name[-1])
    barrio = '_'.join(file_name[1:-1])
    delitos_completos.add((comuna, barrio, año))

print(delitos_completos)
print(len(delitos_completos))

# save set to pickle file
with open('delitos_completados.pickle', 'wb') as handle:
    pickle.dump(delitos_completos, handle, protocol=pickle.HIGHEST_PROTOCOL)
