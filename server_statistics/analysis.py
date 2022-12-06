import numpy as np
import pandas as pd
import re
import os
import datetime


def apply(data_list, func, *kwargs):
    return [func(i, *kwargs) for i in data_list]


def vectorize(func, *kwargs):
    func_vec = np.vectorize(func)
    return func_vec(*kwargs)


class DelayData:
    def __init__(self):
        self.data = None
        self.stations = None  # contains ext and extDir
        self.n = 0

    def read_data(self, path_files, files_raw):
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
            var = [((("s" + str(stations[i][0]) + "_sDir" + str(stations[i][1])) in f) & (".csv" in f)) for f in
                   files_raw]
            files = np.array(files_raw, dtype=str)[var]
            # print("files", files)
            file = os.path.join(path_files, files[len(files) - 1])
            print("open", file)
            data_station = pd.read_csv(file, sep=";", index_col=0, dtype={"line": str, "delay": int, "rideID": str})
            dates = [datetime.datetime.strptime(d[0:19], '%Y-%m-%dT%H:%M:%S') for d in data_station["time_plan"]]
            data_station["time_plan"] = dates

            data.append(data_station)

        self.data = data
        self.stations = stations
        self.n = len(stations)

    def add_features(self):
        self.add_mode()
        self.add_date()
        self.add_hour()

    def get_data(self, i=None):
        if type(i) == type(None):
            return self.data
        else:
            return self.data[i]

    def findMode_raw(self, mode_str, returnType="mode"):
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
            col = "red"
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
        elif len(mode_str) >= 3 and mode_str[0:3] == "HBX":  # Harz-Berlin-Express
            mode = "HBX"
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
                col = "purple"
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

        if returnType == "mode":
            return mode
        elif returnType == "col":
            return col

    def findMode(self, *args, **kwargs):
        func = np.vectorize(self.findMode_raw)
        return func(*args, **kwargs)

    def findColor(self, data_station=None, subset_index=0):
        # need to provide either data_station or subset_index of instance data.
        if type(data_station) == type(None):
            data_station = self.data[subset_index]
        return self.findMode(data_station["line"], returnType="col")

    def get_hours(self, subset_index=False):
        if "hour" not in self.data[0].keys():
            self.add_hour()
        if subset_index is not None:
            data_station = self.data[subset_index]
            return data_station["hour"]
        else:
            return [data_station["hour"] for data_station in self.data]

    def add_mode(self):
        def add_mode_raw(data_station):
            modes = self.findMode(data_station["line"])
            data_station.insert(6, "mode", modes)  # add column to data frame
            return data_station

        self.data = apply(self.data, add_mode_raw)

    def add_date(self):
        def add_date_raw(data_station):
            dates = [i.date() for i in data_station["time_plan"]]
            data_station.insert(7, "date", dates)  # add column to data frame
            return (data_station)

        self.data = apply(self.data, add_date_raw)

    def add_hour(self):
        def add_hour_raw(data_station):
            hours = np.array([j.hour for j in data_station["time_plan"]])
            data_station.insert(8, "hour", hours)
            return data_station

        self.data = apply(self.data, add_hour_raw)

    def get_mode(self, i=None):
        data = self.get_data(i)
        if i is None:
            print("WARNING. get_mode does not work for i=None yet.")
            exit()
        return data["mode"]