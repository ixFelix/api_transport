import requests, json
import time
import datetime
import numpy as np
import xmltodict
import threading
import platform

# if true, lcd will not be addressed:
debugging = platform.system() == "Windows"  # if windows, then debugging

if not debugging:
    import lcddriver
    lcd = lcddriver.lcd()

if debugging:
    path_to_owm_token = "owm_token.txt"
else:
    path_to_owm_token = "/home/pi/work/projects/api_transport/lcd_display/owm_token.txt"

t1 = time.time()
print(" ========= begin of file", datetime.datetime.now(), "==========")
INTERVALL_print = 10
INTERVALL_request = 60
INTERVAL_owm = 60 * 10  # 10 min temporal resolution of model
WORKTIME_HOURS = [[8, 10]]

baseurl_vbb = "https://v6.vbb.transport.rest/"
urlending = "&accept=application/x-ndjson"
station1 = '900070401'  # Tauernallee Saentisstrasse
direction1 = '900070301'  # Alt-Mariendorf
direction2 = '900082202'  # Johannisthaler Chaussee

newest_next_departures = {}


def responseToDict(response, return_json=True):
    if return_json:
        return json.loads(response)
    else:
        return xmltodict.parse(response)


def openWebsite(address):
    print(address)
    try:
        r = requests.get(address)
    except requests.exceptions.MissingSchema as e:
        print(" - Error in Request (Missing  Schema):", e)
    except requests.exceptions.ConnectionError as e:
        print(" - Error in Request (ConnectionError. Does page exist?):", e)
    else:
        return r.text


def online_next_departures(station=station1, direction=direction1):
    address = "https://v6.vbb.transport.rest/stops/" + station + "/departures?/&direction=" + direction + "&results" \
                                                                                                          "=6&duration=20&accept=application/x-ndjson"
    response_xml = openWebsite(address)
    if response_xml is None:
        print("Warning: response is empty (None).")
        return ""
    if len(response_xml) == 0:
        print("Warning: response is empty (len 0).")
        return ""
    else:
        global newest_next_departures
        if station not in newest_next_departures.keys():
            print(" - add station")
            newest_next_departures[station] = {}

        newest_next_departures[station][direction] = responseToDict(response_xml)
    #update_lines()


def print_lcd(message="", lineNo=0, print_debug=""):
    if print_debug != "":
        print(print_debug)
    print(" lcd line " + str(lineNo) + ": " + message + " (len:" + str(len(message)) + ")")
    if len(message) > 20:
        message = message[0:20]
    if not debugging:
        lcd.lcd_display_string(message, lineNo+1)


def update_lines():
    for i in range(4):
        update_line(i)


def update_line(lineNo=0):
    def lcd_empty_line(message=""):
        print(message)

    if lineNo in [0, 1, 2]:
        # check conditions
        if station1 not in newest_next_departures.keys() or direction1 not in newest_next_departures[station1] \
                or 'departures' not in newest_next_departures[station1][direction1].keys():
            print_lcd("(no data)            ", print_debug="Lines 0+1: key direction1 in response not available")
            return None
        if lineNo == 2:  # check whether other direction worked
            if station1 not in newest_next_departures.keys() or direction2 not in newest_next_departures[station1] \
                    or 'departures' not in newest_next_departures[station1][direction2].keys():
                print_lcd("(no data)            ", print_debug="Line 2: key direction2 in response not available")
                return None

        # extract information
        def extract_departures(nextDep, noDeps):
            info_show_dir = {"iLine": [None for i in range(noDeps)],
                             "iDest": [None for i in range(noDeps)],
                             "diffMin": [None for i in range(noDeps)]}

            if len(nextDep) < noDeps:
                print("next Departures. number of Deps too short")
                # todo: handle that progroam does not continue with None!
                return False
            now = datetime.datetime.now()
            for i in range(noDeps):
                iLine = nextDep[i]['line']['name']
                iDest = nextDep[i]['direction'][0:12]
                iTime = nextDep[i]['when']
                iWait = datetime.datetime.strptime(iTime[0:19],
                                                   '%Y-%m-%dT%H:%M:%S') - now
                if iWait.seconds > 24 * 60 * 60 / 2:
                    diffMin = (24 * 60 * 60 - iWait.seconds) // 60
                else:
                    diffMin = iWait.seconds // 60
                info_show_dir["iLine"][i], info_show_dir["iDest"][i], info_show_dir["diffMin"][
                    i] = iLine, iDest, diffMin
            return info_show_dir

        if lineNo in [0, 1, 2]:
            nextDep = newest_next_departures[station1][direction1]["departures"]
            info_show_dir1 = extract_departures(nextDep, 4)

        if lineNo == 2:
            nextDep = newest_next_departures[station1][direction2]["departures"]
            info_show_dir2 = extract_departures(nextDep, 1)

        # print line
        final_str = "(no data)           "
        if lineNo in [0, 1] and info_show_dir1:
            final_str = info_show_dir1["iLine"][lineNo].ljust(3) + " " + info_show_dir1["iDest"][lineNo].ljust(11) + \
                        " " + str(info_show_dir1["diffMin"][lineNo]).rjust(2) + ""
        if lineNo == 2 and info_show_dir1 and info_show_dir2:
            final_str = info_show_dir1["iLine"][2][0:1] + ":" + str(info_show_dir1["diffMin"][2]) + ", " + \
                        info_show_dir1["iLine"][3][0:1] + ":" + str(info_show_dir1["diffMin"][3]) + \
                        ", X71*:" + str(info_show_dir2["diffMin"][0]) + "  "

        print_lcd(final_str, lineNo)

    if lineNo == 3:
        if station1 not in newest_next_departures.keys() or direction1 not in newest_next_departures[station1] \
                or 'realtimeDataUpdatedAt' not in newest_next_departures[station1][direction1].keys():
            print_lcd("(no delay data)     ", lineNo=3,
                      print_debug="line 3: no delay data yet or key missing")
            return None
        iLast_raw = newest_next_departures[station1][direction1]["realtimeDataUpdatedAt"]
        iDelta = datetime.datetime.now() - datetime.datetime.fromtimestamp(iLast_raw)
        final_str = " (delay: " + str(iDelta.seconds) + "s) "
        print_lcd(final_str, lineNo)


def request_timer(wait=INTERVALL_request):
    # repeatedly start requests. This function should be called in an "outer" thread and contains "inner" threads.
    x1 = threading.Thread(target=online_next_departures, args=(station1, direction1))
    x2 = threading.Thread(target=online_next_departures, args=(station1, direction2))

    count_loops_1 = 0
    while True:

        # check working time
        now = datetime.datetime.now()
        worktime_i=0
        if now.hour < WORKTIME_HOURS[worktime_i][0] or now.hour > WORKTIME_HOURS[worktime_i][1]:
            print("outside of working ours. sleep for ", wait, "s.")
            print_lcd("                    ", 0)
            print_lcd("   Good Night :)    ", 1)
            print_lcd("                    ", 2)
            print_lcd("                    ", 3)
            time.sleep(wait)
            continue

        print("  - begin of request loop (" + str(count_loops_1) + "). Time: ", datetime.datetime.now())
        if not x1.is_alive():
            print(" start thread 1")
            x1 = threading.Thread(target=online_next_departures, args=(station1, direction1))
            x1.start()
        else:
            print(" do not start thread 1 because it is still running")

        if not x2.is_alive():
            print(" start thread 2")
            x2 = threading.Thread(target=online_next_departures, args=(station1, direction2))
            x2.start()
        else:
            print(" do not start thread 2 because it is still running")
        count_loops_1 += 1
        print("  sleep request for ", INTERVALL_request, "s.")
        time.sleep(wait)


def print_timer(wait=INTERVALL_print):
    count_loops = 0
    while True:
        now = datetime.datetime.now()
        worktime_i=0
        if now.hour < WORKTIME_HOURS[worktime_i][0] or now.hour > WORKTIME_HOURS[worktime_i][1]:
            time.sleep(wait)
            continue

        print("  - begin of print loop (" + str(count_loops) + "). Time: ", datetime.datetime.now())
        update_lines()
        print(" sleep for ", INTERVALL_print, "s.")
        time.sleep(wait)
        count_loops += 1


# main script

thread_print = threading.Thread(target=print_timer, args=(INTERVALL_print,))  # every x seconds
thread_requests = threading.Thread(target=request_timer, args=(INTERVALL_request,))  # every y seconds

thread_print.start()
thread_requests.start()
