import time
import datetime
import numpy as np
import api_handler
import pandas as pd
import os

path_wd = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

t1 = time.time()
now = datetime.datetime.now()
print("================== start script (" + str(now) + ") =====================")

# ["Tauernallee Santisstrasse", "s+U Berlin Hauptbahnhof", ...
ext_list = [900070401, 900003201]
# ["U Alt-Mariendorf", False, ...
ext_dir_list = [900070301, False]
data = [None for i in range(len(ext_list))]

pd.set_option('display.max_columns', 9)

# read data from earlier run and remove files that do not match ext, ext_dir, "_h" and ".csv"
#files = os.listdir(path_wd + "\\records\\hourly\\")
files_raw = os.listdir(os.path.join(path_wd, "records/hourly/"))
files_raw.sort()
print("all files",files_raw)
for station_i in range(len(data)):
    var = [((("s" + str(ext_list[station_i]) + "_sDir" + str(ext_dir_list[station_i])) in f) & ("_h" in f) & (".csv" in f)) for f in files_raw]
    print("var", var)
    files = np.array(files_raw, dtype=str)[var]
    print(station_i, files)
    if len(files)>0:
        #data = pd.read_csv(path_wd + "\\records\\hourly\\" + files[len(files) - 1], sep=";", index_col=0, dtype=str)
        data[station_i] = pd.read_csv(os.path.join(path_wd, "records/hourly/", files[len(files) - 1]), sep=";", index_col=0, dtype=str)
    else:
        data[station_i] = pd.DataFrame()

j=0
while True:
#if True:
#for j in range(100):
    print("  - begin of loop (" + str(j) + "). Time: ", time.time())
    t_loop = time.time()

    for station_i in range(len(ext_list)):
        ext, ext_dir = ext_list[station_i], ext_dir_list[station_i]
        print("------------- \n handle station nr", station_i,"(",ext,")")
        #print("content of loaded file:")
        #print(data[data_i])
        try:
            nextDep = api_handler.nextDeparturesAtStop(ext=ext, maxNo=30, duration=5, ext_dir=ext_dir)

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

            #print(data_dummy)
            # combine old and new data and remove duplicates
            data_new = pd.DataFrame(data_dummy)
            #print("data new\n", data_new)
            data[station_i] = pd.concat([data[station_i], data_new], ignore_index=True)
            #print("combined old data + new data\n", data[station_i])
            data[station_i] = data[station_i].drop_duplicates(keep="last", subset=["time_plan", "rideID"])#, inplace=True)
            data[station_i] = data[station_i].sort_values(by="time_plan", axis=0)
            #print("combined data without duplicates\n", data)

            # save files in 3 different time scales to make sure, not all data is deleted.
            # delete hourly and daily saves from time to time.
            print("found",len(nextDep),"results. Store them in csv. print first new data:")
            print(iTime, iLine, iDest,iDelay, iRideID)
            data[station_i].to_csv(os.path.join(
                path_wd, "records/hourly/s" + str(ext) + "_sDir" + str(ext_dir) + "_d" + str(now)[0:10] + "_h" + str(now)[11:13] + ".csv"),
                sep=";")
            data[station_i].to_csv(os.path.join(
                path_wd, "records/daily/" + "s" + str(ext) + "_sDir" + str(ext_dir) + "_d" + str(now)[0:10] + ".csv"),
                sep=";")
            data[station_i].to_csv(os.path.join(
                path_wd, "records/monthly/" + "s" + str(ext) + "_sDir" + str(ext_dir) + "_d" + str(now)[0:7] + ".csv"),
                sep=";")

        except Exception as e:
            print(" - Error in Request:", e)

    time.sleep(3 * 60)
    #time.sleep(3)
    j=j+1

print("end of script. Total runtime =", time.time() - t1)
