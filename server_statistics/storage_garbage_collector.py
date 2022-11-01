# Check stored csv files for completeness. Usually, all but the newest files can be deleted.
# I will leave the last 3 for security reasons.

import os
import sys
import re
import numpy as np
import pandas as pd

path_wd = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
arguments = sys.argv
if len(arguments) > 1:
    frequency = arguments[1]
else:
    frequency = "daily"

path_files = os.path.join(path_wd, 'records/'+frequency)

files_raw = os.listdir(path_files)

# remove non-csv files (e.g. trash folder)
csvFiles = [(".csv" in f) for f in files_raw]
files_raw = np.array(files_raw)[csvFiles]

files_raw.sort()
print("all files")
print(files_raw)

# collect ext and dir:
ext_extDir_list = []
for f_i in range(len(files_raw)):
    ext = re.search('s(.*)_sDir', files_raw[f_i])
    extDir = re.search('sDir(.*)_d20', files_raw[f_i])
    if ext is not None:
        ext_extDir_list.append((ext.group(1), extDir.group(1)))

stations = list(set([i for i in ext_extDir_list]))
print("stations", stations)

# load all data for one station
data =[]
print(files_raw)
for i in range(len(stations)):
    var = [((("s" + str(stations[i][0]) + "_sDir" + str(stations[i][1])) in f) & (".csv" in f)) for f in files_raw]
    print(var)
    files = np.array(files_raw, dtype=str)[var]
    print("files", files)
    data_station = []
    for f_i in range(len(files)):
        if len(files[f_i])>0:
            data_station.append(pd.read_csv(os.path.join(path_files, files[f_i]), sep=";", index_col=0, dtype=str))
        else:
            print("no files found for this station!")
    data.append(data_station)

# check whether each file is a subset of the next newer file (no data is lost in newer file)
save_delete_list=[]
for j in range(len(stations)):
    save_delete_station = []
    for i in range(len(data[j])-1):
        if len(data[j][i+1].merge(data[j][i], on=["time_plan", "rideID"])) == len(data[j][i]):
            print(i, i+1, "correct")
            save_delete_station.append(True)
        else:
            print(i, i+1, "error. no subset.")
            save_delete_station.append(False)

    if len(data[j]) >= 2:
        save_delete_station[len(save_delete_station) - 1] = False  # never deleted second-newest file
    save_delete_station.append(False)  # never delete newest file
    save_delete_list.append(save_delete_station)

# determine files to delete
print("\n Delete? ")
delete_list_final = []
for i in range(len(stations)):
    var = [((("s" + str(stations[i][0]) + "_sDir" + str(stations[i][1])) in f) & (".csv" in f)) for f in files_raw]
    files = np.array(files_raw, dtype=str)[var]

    for j in range(len(files)):
        print(save_delete_list[i][j], files[j])
        if save_delete_list[i][j]:
            delete_list_final.append(files[j])

print("\n Final delete (might be empty):")
[print(i) for i in delete_list_final]

# move files in delete folder
print("\n commands (might be empty):")
for f in delete_list_final:
    print(os.path.join(path_files,f), os.path.join(path_files,"trash",f))
    #os.rename(os.path.join(path_files,f), os.path.join(path_files,"trash",f))

print(" -- End of script :) --")