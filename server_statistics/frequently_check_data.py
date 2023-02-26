import emailSender as email
import numpy as np
import os
import datetime

number_stations = 2  # number of stations
size_threshold = 1000  # report when one of  newest file is smaller

# get filenames
path_wd = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
path_files = os.path.join(path_wd, 'records/hourly/')
files_raw = np.array(os.listdir(path_files))

# get two newest files:
times = np.array([os.path.getctime(os.path.join(path_files, f)) for f in files_raw])
order = np.argsort(times)
newest2 = files_raw[order[[-1, -2]]]

report = ""

# ------- check their size --------
sizes = np.array([os.path.getsize(os.path.join(path_files, i)) for i in newest2])
if any(sizes < size_threshold):
    idx = np.where(sizes < size_threshold)[0][0]
    report += "\n - At least one file is smaller than " + str(size_threshold) + ". That is suspicious. File=" +\
              str(files_raw[idx])

# -------- check time --------
try:
    now = datetime.datetime.now()
    nowH = now.hour
    for i in range(number_stations):
        if newest2[i][-7:-6] != "h":
            report += "\n - error in name of newest file, 'h' not found. File=" + \
                     str(newest2[i]) + ", nowH=" + str(nowH)
        else:
            h = int(newest2[i][-6:-4])
            if not (nowH == h or nowH == (h + 1) % 24):
                report += "\n - newest file is older than 1 hour. File=" + str(newest2[i]) + \
                         ", h=" + str(h) + ", nowH=" + str(nowH)
except:
    report += "\n - general problem in frequently_check_data.py --> check time"

print(report)
# nowH 5, h 3 not ok!
# nowH 5, h 4 ok
# nowH 5, h 5 ok
# nowH 5, h 6 not ok!

# nowH 0, h 22 not ok!
# nowH 0, h 23 ok
# nowH 0, h 0 ok
# nowH 0, h 1 not ok


subject = "Report of problem in api_transport"
message_text = report
email.send_message(subject=subject, message_text=message_text, to="ident_green@posteo.de")
