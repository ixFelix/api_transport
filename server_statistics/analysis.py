import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime


path_wd = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
path_files = os.path.join(path_wd, 'records/hourly/')
files_raw = os.listdir(path_files)

print(files_raw)

files_raw.sort()

# collect ext and dir:
ext_extDir_list = []
for f_i in range(len(files_raw)):
    ext = re.search('s(.*)_sDir', files_raw[f_i])
    extDir = re.search('sDir(.*)_d20', files_raw[f_i])
    if ext is not None:
        ext_extDir_list.append((ext.group(1), extDir.group(1)))

stations = list(set([i for i in ext_extDir_list]))

data =[]
#print(files_raw)
for i in range(len(stations)):
    var = [((("s" + str(stations[i][0]) + "_sDir" + str(stations[i][1])) in f) & (".csv" in f)) for f in files_raw]
    files = np.array(files_raw, dtype=str)[var]
    #print("files", files)
    file = os.path.join(path_files, files[len(files)-1])
    print("open", file)
    data_station =pd.read_csv(file, sep=";", index_col=0, dtype={"line": np.str, "delay": np.int, "rideID": np.str})
    dates = [datetime.datetime.strptime(d[0:19], '%Y-%m-%dT%H:%M:%S') for d in data_station["time_plan"]]
    data_station["time_plan"] = dates

    data.append(data_station)


# print histogram
i = 0
data_station = data[i]
f = plt.figure()
plt.plot(data_station["time_plan"], data_station["delay"])
f.savefig("plots/time_series.pdf", bbox_inches='tight')