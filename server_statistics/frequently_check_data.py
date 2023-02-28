import emailSender as email
import numpy as np
import os
import datetime

number_stations = 2  # number of stations
size_threshold = 1000  # report when one of  newest file is smaller
send_mail_switch = True

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
print("check sizes")
sizes = np.array([os.path.getsize(os.path.join(path_files, i)) for i in newest2])
print("... sizes:", sizes)
if any(sizes < size_threshold):
    idx = np.where(sizes < size_threshold)[0][0]
    report += "\n - At least one file is smaller than " + str(size_threshold) + ". That is suspicious. File=" +\
              str(newest2[idx])
    print("... problem in sizes. see report.")
else:
    print("... sizes ok.")

# -------- check time --------
print("check time")
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
else:
    print("... times ok.")


# ------ handle report sending -------

subject = "Report of problem in api_transport"


# debug. always send email.
# email.send_message(subject=subject, message_text=report, to="ident_green@posteo.de")
# end of debug

print(report)
if len(report) == 0:
    print("Everything is fine. Nothing to report. No email sent.")
else:
    if send_mail_switch:
        email.send_message(subject=subject, message_text=report, to="ident_green@posteo.de")
