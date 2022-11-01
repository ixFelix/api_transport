# Check stored csv files for completeness. Usually, all but the newest files can be deleted.
# I will leave the last 3 for security reasons.

import os
import re
import numpy as np
import pandas as pd

#path_wd = "/home/pi/work/api_transport/server_statistics/"
#path_wd = "D:\\implementations\\api_transport\\server_statistics\\"
path_wd = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

path_files = os.path.join(path_wd, 'records/hourly')

#print(current_wd)

files_raw = os.listdir(path_files)
files_raw.sort()
print("all files")
print(files_raw)

# collect ext and dir:
ext_extDir_list = []
for f_i in range(len(files_raw)):
    ext = re.search('s(.*)_sDir', files_raw[f_i])
    extDir = re.search('sDir(.*)_d20', files_raw[f_i])
    ext_extDir_list.append((ext.group(1), extDir.group(1)))

stations = list(set([i for i in ext_extDir_list]))
print("stations", stations)

# load all data for one station
data =[]
for i in range(len(stations)):
    var = [((("s" + str(stations[i][0]) + "_sDir" + str(stations[i][1])) in f) & ("_h" in f) & (".csv" in f)) for f in files_raw]
    #print("var", var)
    files = np.array(files_raw, dtype=str)[var]
    #print(i, files)
    data_station = []
    for f_i in range(len(files)):
        if len(files[f_i])>0:
            data_station.append(pd.read_csv(os.path.join(path_files, files[f_i]), sep=";", index_col=0, dtype=str))
        else:
            print("no files found for this station!")
    data.append(data_station)

save_delete_list=[]
for j in range(len(stations)):
    save_delete_station = []
    for i in range(len(data[j])-1):
        # print(len(data[j][i+1]))
        # print(len(data[j][i]))
        # print(len(data[j][i+1].merge(data[j][i], on=["time_plan", "rideID"])))
        if len(data[j][i+1].merge(data[j][i], on=["time_plan", "rideID"])) == len(data[j][i]):
            print(i, i+1, "correct")
            save_delete_station.append(True)
        else:
            print(i, i+1, "error. no subset.")
            save_delete_station.append(False)

    save_delete_station[len(save_delete_station)-1] = False  # never deleted second-newest file
    save_delete_station.append(False)  # never delete newest file
    save_delete_list.append(save_delete_station)

#print(save_delete_list)

print("\n Delete? ")
delete_list_final = []
for i in range(len(stations)):
    var = [((("s" + str(stations[i][0]) + "_sDir" + str(stations[i][1])) in f) & ("_h" in f) & (".csv" in f)) for f in files_raw]
    #print("var", var)
    files = np.array(files_raw, dtype=str)[var]

    for j in range(len(files)):
        print(save_delete_list[i][j], files[j])
        if save_delete_list[i][j]:
            delete_list_final.append(files[j])

print("\n Final delete:")
[print(i) for i in delete_list_final]



"""print(len(data[0])

print(data[1])
#merged = \
data[1].merge(data[0])
print(data[1])
#merged.drop_duplicates(keep="last", subset=["time_plan", "rideID"])
#data[station_i] = data[station_i].drop_duplicates()  # , inplace=True)

#print(len(merged))#"""