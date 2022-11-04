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
def findMode(mode_str, returnType="mode"):
    # input: str of line, e.g.: "ICE 704"
    # returnType can be: "mode" (returns str of mode), "col" (returns str of color)
    if mode_str[0] == "U":  # U-Bahn
        mode = "U"
        col = "blue"
    elif mode_str[0] == "S":  # S-Bahn
        mode = "S"
        col = "green"
    elif mode_str[0:2] == "RE":  # Regionaexpress
        mode = "RE"
        col = "red"
    elif mode_str[0:2] == "RB":  # Regionalbahn
        mode = "RB"
        col ="red"
    elif mode_str[0:2] == "IC":  # Intercity
        mode = "IC"
        col = "orange"
    elif mode_str[0:2] == "EC":  # Eurocity
        mode = "EC"
        col = "orange"
    elif mode_str[0:2] == "EN":  # Euronight
        mode = "EN"
        col = "orange"
    elif mode_str[0:2] == "NJ":  # Nightjet
        mode = "NJ"
        col = "orange"
    elif mode_str[0:2] == "RJ":  # Railjet
        mode = "RJ"
        col = "orange"
    elif len(mode_str) >= 3 and mode_str[0:3] == "FEX":  # Flughafenexpress
        mode = "FEX"
        col = "red"
    elif len(mode_str) >= 3 and mode_str[0:3] == "FLX":  # Flixtrain
        mode = "FLX"
        col = "orange"
    elif len(mode_str) >= 3 and mode_str[0:3] == "ICE":  # Intercity-Express
        mode = "ICE"
        col = "orange"
    elif mode_str[0] == "M":  # Metro bus or metro tram
        if len(mode_str) == 2 or (len(mode_str) == 3 and mode_str[1:3] in [10, 13, 17]):
            mode = "MT"  # metro tram
            col = "red"
        else:
            mode = "MB"  # metro bus
            col = "purple"
    elif mode_str[0] == "N":
        if (len(mode_str) == 2 and mode_str[1].isnumeric()) or (len(mode_str) == 3 and mode_str[1:3].isnumeric()):
            mode = "NB"  # Night Bus
            col ="purple"
    elif len(mode_str) >= 3 and mode_str.isnumeric():  # Bus
        mode = "B"
        col = "purple"
    elif mode_str[0] == "X":  # Express-Bus
        mode = "XB"
        col = "purple"

    else:
        print("found no mode for line", mode_str)
        mode = "999"
        col = "grey"

    if returnType=="mode":
        return mode
    elif returnType=="col":
        return col
findMode_vec = np.vectorize(findMode)

for i in range(len(stations)):
    data_station = data[i]
    modes = findMode_vec(data_station["line"])
    data_station.insert(6, "mode",modes) # add column to data frame
    #print(modes)
    data[i] = data_station


def plot_timeSeries():
    fig = plt.figure()
    for i in range(len(stations)):
        data_station = data[i]
        colors = findMode_vec(data_station["line"], returnType="col")

        ax = fig.add_subplot(2, 1, i + 1)
        ax.plot(data_station["time_plan"], np.zeros(len(data_station)), c="black", linewidth=0.5)
        ax.scatter(data_station["time_plan"], data_station["delay"], alpha=1, c=colors, s=0.1 )
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

def plot_histogram():
    fig = plt.figure()
    for i in range(len(stations)):
        data_station = data[i]
        ax = fig.add_subplot(2, 1, i + 1)
        ax.hist(data_station["delay"], bins=20)
    plt.show()

def plot_delayVsHour():
    fig = plt.figure()
    for i in range(len(stations)):
        data_station = data[i]
        hours = [j.hour for j in data_station["time_plan"]]

        ax = fig.add_subplot(2, 1, i + 1)
        ax.scatter(hours, data_station["delay"])
        # boxplot expects data=(ArrayHour1, ArrayHour2, ArrayHour3)
    plt.show()

#plot_timeSeries()
#plot_histogram()
plot_delayVsHour()
