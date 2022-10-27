import os.path
import time
import datetime
import numpy as np
from server_statistics import api_handler
import pandas as pd
import os


path_wd = os.getcwd()# + "\\server_statistics\\"

t1 = time.time()

ext = 900070401  # "Tauernallee Santisstrasse"
ext_dir = 900070301  # U Alt-Mariendorf


pd.set_option('display.max_columns', 9)




# read data from earlier run and remove files that do not match ext, ext_dir, "_h" and ".csv"
files = os.listdir(path_wd + "\\records\\hourly\\")
var = [((("s" + str(ext) + "_sDir" + str(ext_dir)) in f) & ("_h" in f) & (".csv" in f)) for f in files]
files = np.array(files, dtype=str)[var]

if len(files)>0:
    data = pd.read_csv(path_wd + "\\records\\hourly\\" + files[len(files) - 1], sep=";", index_col=0, dtype=str)
else:
    data = pd.DataFrame()

# while True:
#if True:
for j in range(100):
    print("  - begin of loop (" + str(j) + "). Time: ", time.time() - t1)
    t_loop = time.time()

    try:
        nextDep = api_handler.nextDeparturesAtStop(ext=ext, maxNo=10, ext_dir=ext_dir)

        now = datetime.datetime.now()
        data_dummy = []

        for i in range(len(nextDep)):  # for each departure event in this request

            # extract information
            iLine = nextDep[i]['line']['name']
            iDest = nextDep[i]['direction']  # [0:12]
            iTime_plan = nextDep[i]['plannedWhen']
            iTime = nextDep[i]['when']
            iRideID = nextDep[i]['line']['fahrtNr']  # HAS A BUG. X76 always with same ID

            # handle dates and delay
            iTime_plan_data = datetime.datetime.strptime(iTime_plan[0:19], '%Y-%m-%dT%H:%M:%S')
            iTime_date = datetime.datetime.strptime(iTime[0:19], '%Y-%m-%dT%H:%M:%S')
            iDelay_date = iTime_date - iTime_plan_data
            if iDelay_date.seconds > 24 * 60 * 60 / 2:
                iDelay = - (24 * 60 * 60 - iDelay_date.seconds) / 60
            else:
                iDelay = str(iDelay_date.seconds / 60)

            # add row for this data point
            data_dummy.append({"time_plan": iTime_plan, "line": iLine, "dest": iDest, "delay": iDelay,
                               "request": str(now)[0:19], "rideID": iRideID})

        # combine old and new data and remove duplicates
        data_new = pd.DataFrame(data_dummy)
        #print("data new\n", data_new)
        data = pd.concat([data, data_new], ignore_index=True)
        #print("combined old data + new data\n", data)
        data = data.drop_duplicates(keep="last", subset=["time_plan", "rideID"])#, inplace=True)
        data = data.sort_values(by="time_plan", axis=0)
        #dups = data.duplicated(keep="last", subset=["time_plan", "rideID"])
        #data_noDups = data[dups]
        #print("combined data without duplicates\n", data)

        # save files in 3 different time scales to make sure, not all data is deleted.
        # delete hourly and daily saves from time to time.
        data.to_csv("records/hourly/" + "s" + str(ext) + "_sDir" + str(ext_dir) + "_d" + str(now)[0:10] + "_h" + str(now)[11:13] + ".csv",sep=";")
        #data.to_csv("records/daily/" + "s" + str(ext) + "_sDir" + str(ext_dir) + "_d" + str(now)[0:10] + ".csv",sep=";")
        # data.to_csv("records/monthly/" + "s" + str(ext) + "_sDir" + str(ext_dir) + "_d" + str(now)[0:7] + ".csv", sep=";")

    except Exception as e:
        print(" - Error in Request:", e)
    time.sleep(3 * 60)
    #time.sleep(3)

print("end of script. Total runtime =", time.time() - t1)
