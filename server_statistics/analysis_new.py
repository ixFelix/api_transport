import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime

plot_pdf = False

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

# open all files
data = []
for i in range(len(stations)):
    var = [((("s" + str(stations[i][0]) + "_sDir" + str(stations[i][1])) in f) & (".csv" in f)) for f in files_raw]
    files = np.array(files_raw, dtype=str)[var]
    # print("files", files)
    file = os.path.join(path_files, files[len(files) - 1])
    print("open", file)
    data_station = pd.read_csv(file, sep=";", index_col=0, dtype={"line": str, "delay": int, "rideID": str})
    dates = [datetime.datetime.strptime(d[0:19], '%Y-%m-%dT%H:%M:%S') for d in data_station["time_plan"]]
    data_station["time_plan"] = dates

    data.append(data_station)


# process data
def findMode(mode_str):
    if mode_str[0] == "U":  # U-Bahn
        return "U"
    elif mode_str[0] == "S":  # S-Bahn
        return "S"
    elif mode_str[0:2] == "RE":  # Regionaexpress
        return "RE"
    elif mode_str[0:2] == "RB":  # Regionalbahn
        return "RB"
    elif mode_str[0:2] == "IC":  # Intercity
        return "IC"
    elif mode_str[0:2] == "EC":  # Eurocity
        return "EC"
    elif mode_str[0:2] == "EN":  # Euronight
        return "EN"
    elif mode_str[0:2] == "NJ":  # Nightjet
        return "NJ"
    elif mode_str[0:2] == "RJ":  # Railjet
        return "RJ"
    elif len(mode_str) >= 3 and mode_str[0:3] == "FEX":  # Flughafenexpress
        return "FEX"
    elif len(mode_str) >= 3 and mode_str[0:3] == "FLX":  # Flixtrain
        return "FLX"
    elif len(mode_str) >= 3 and mode_str[0:3] == "ICE":  # Intercity-Express
        return "ICE"
    elif mode_str[0] == "M":  # Metro bus or metro tram
        if len(mode_str) == 2 or (len(mode_str) == 3 and mode_str[1:3] in [10, 13, 17]):
            return ("MT")  # metro tram
        else:
            return ("MB")  # metro bus
    elif mode_str[0] == "N":
        if (len(mode_str) == 2 and mode_str[1].isnumeric()) or (len(mode_str) == 3 and mode_str[1:3].isnumeric()):
            return ("NB")  # Night Bus
    elif len(mode_str) >= 3 and mode_str.isnumeric():  # Bus
        return "B"
    elif mode_str[0] == "X":  # Express-Bus
        return "XB"

    else:
        print("found no mode for line", mode_str)
        return "999"


findMode_vec = np.vectorize(findMode)

for i in range(len(stations)):
    data_station = data[i]
    modes = findMode_vec(data_station["line"])
    # add column to data frame
    print(modes)

    data[i] = data_station

# print histogram
fig = plt.figure()
for i in range(len(stations)):
    data_station = data[i]

    ax = fig.add_subplot(2, 1, i + 1)
    ax.plot(data_station["time_plan"], np.zeros(len(data_station)), c="black", linewidth=0.5)
    ax.scatter(data_station["time_plan"], data_station["delay"], alpha=0.2, c="red")
    if i == 0:
        ax.set_xticklabels(())
    # if i==1:
    ax.margins(x=0)
    plt.xticks(fontsize=10, rotation=45)
fig.tight_layout()

if plot_pdf:
    save_file = "plots/time_series_s" + stations[i][0] + "_sDir" + stations[i][1] + ".png"
    print("saving", save_file)
    fig.savefig(save_file, bbox_inches='tight')
