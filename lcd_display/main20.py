# bug notice: The lcd display does not work when new lines are sent from different threads. Therefore, I only send data
# from the print thread and never from the requests thread.

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
WORKTIME_HOURS = [[0,24]]

baseurl_vbb = "https://v6.vbb.transport.rest/"
urlending = "&accept=application/x-ndjson"
#station1 = '900070401'  # Tauernallee Saentisstrasse
#direction1 = '900070301'  # Alt-Mariendorf
#direction2 = '900082202'  # Johannisthaler Chaussee
station1   = '900066102' # Botanischer Garten
direction1 = '900054104' # Schoeneberg
station2   = '900066405' # Hindenburgdamm Klingsorstrasse
direction2 = '900062202' # Rathaus Steglitz
MIN_WAIT_FIRST_STATION = 9   # lines 0-1 (station1)
MIN_WAIT_SECOND_STATION = 5  # lines 2-3 (station2)

newest_next_departures = {}
departures_lock = threading.Lock()

current_prints = [None, None, None, None] # save current print and do not reprint if no change.

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
    address = "https://v6.vbb.transport.rest/stops/" + station + "/departures?/&direction=" + direction + "&duration=60&accept=application/x-ndjson"
    response_xml = openWebsite(address)
    if response_xml is None:
        print("Warning: response is empty (None).")
        return ""
    if len(response_xml) == 0:
        print("Warning: response is empty (len 0).")
        return ""
    else:
        global newest_next_departures
        data = responseToDict(response_xml)

        with departures_lock:   # NEW
            if station not in newest_next_departures:
                print(" - add station")
                newest_next_departures[station] = {}
            newest_next_departures[station][direction] = data
    #update_lines()


def print_lcd(message="", lineNo=0, print_debug=""):
    if print_debug != "":
        print(print_debug)

    # force exactly 20 characters (prevents leftover chars on LCD)
    message = (message or "").ljust(20)[:20]

    print(" - lcd line " + str(lineNo) + ": " + message + " (len:" + str(len(message)) + ")")

    if current_prints[lineNo] == message:
        print("    (already printed. do not send again)")
        return None
    else:
        current_prints[lineNo] = message

    if not debugging:
        lcd.lcd_display_string(message, lineNo+1)

def update_lines():
    for i in range(4):
        update_line(i)


def update_line(lineNo=0):
    print(lineNo)
    stationHere = {0: station1, 1: station1, 2: station2, 3:station2}[lineNo]
    directionHere = {0: direction1, 1: direction1, 2: direction2, 3: direction2}[lineNo]
    if True:#lineNo in [0, 1, 2]:
        # check conditions
        with departures_lock:
            station_block = newest_next_departures.get(stationHere)
            dir_block = station_block.get(directionHere) if station_block else None
            departures = dir_block.get("departures") if dir_block else None

    # --- if not available yet: print placeholder instead of returning silently (NEW) ---
        if not departures:
            print_lcd("(loading)           ", lineNo)
            return None

        def extract_departures(nextDep, noDeps, min_wait_min=0):
            info_show_dir = {"iLine": [], "iDest": [], "diffMin": []}

            now = datetime.datetime.now()

            def clean_dest(dest: str) -> str:
                # requirement (b): remove prefixes
                # order matters: remove the longer token first
                return (dest or "").replace("S+U ", "").replace("S ", "").replace("U ", "").replace("Bhf","")

            for dep in nextDep:
                # stop when we collected enough departures
                if len(info_show_dir["iLine"]) >= noDeps:
                    break

                iLine = dep.get('line', {}).get('name')
                raw_dest = dep.get('direction') or ""
                iDest = clean_dest(raw_dest)[0:12]

                iTime = dep.get('when') or dep.get('plannedWhen')
                if not iTime:
                    continue  # skip entries without time

                try:
                    dt = datetime.datetime.strptime(iTime[0:19], '%Y-%m-%dT%H:%M:%S')
                except Exception:
                    continue  # skip unparsable time strings

                diffMin = int((dt - now).total_seconds() // 60)

                # ignore departures in the past (or "now")
                if diffMin < 0:
                    continue

                # requirement (a): only keep departures that are at least min_wait_min away
                if diffMin < min_wait_min:
                    continue

                if not iLine:
                    continue

                info_show_dir["iLine"].append(iLine)
                info_show_dir["iDest"].append(iDest)
                info_show_dir["diffMin"].append(diffMin)

            return info_show_dir


        #if lineNo in [0, 1, 2]:
        min_wait = MIN_WAIT_FIRST_STATION if lineNo < 2 else MIN_WAIT_SECOND_STATION

        info_show_dir1 = extract_departures(departures, 2, min_wait_min=min_wait)

        if len(info_show_dir1["iLine"]) == 0:
            print_lcd("(too soon)           ", lineNo)
            return None


        # print line
        dep_index = lineNo % 2   # 0 for lines 0+2, 1 for lines 1+3

        final_str = "(no data)           "
        if len(info_show_dir1["iLine"]) > dep_index:
            line = str(info_show_dir1["iLine"][dep_index])[:3].ljust(3)
            dest = str(info_show_dir1["iDest"][dep_index])[:13].ljust(13)
            mins = str(info_show_dir1["diffMin"][dep_index]).rjust(3)  # width 3!

            final_str = f"{line} {dest}{mins}"  # 3 +1 +13 +3 = 20

        # IMPORTANT: always send exactly 20 chars so old characters don't remain
        final_str = final_str.ljust(20)[:20]

        print_lcd(final_str, lineNo)

        

def request_timer(wait=INTERVALL_request):
    # repeatedly start requests. This function should be called in an "outer" thread and contains "inner" threads.
    x1 = threading.Thread(target=online_next_departures, args=(station1, direction1))
    x2 = threading.Thread(target=online_next_departures, args=(station2, direction2))

    count_loops_1 = 0
    while True:

        # check working time
        now = datetime.datetime.now()
        worktime_i=0
        if now.hour < WORKTIME_HOURS[worktime_i][0] or now.hour > WORKTIME_HOURS[worktime_i][1]:
            print(" - outside of working ours. sleep for ", wait, "s.")
            #print_lcd("                    ", 0)
            #print_lcd("   Good Night :)    ", 1)
            #print_lcd("                    ", 2)
            #print_lcd("                    ", 3)
            time.sleep(wait)
            continue

        print(" ---- begin of request loop (" + str(count_loops_1) + "). Time: ", datetime.datetime.now(), " ----")
        if not x1.is_alive():
            print(" start thread 1")
            x1 = threading.Thread(target=online_next_departures, args=(station1, direction1))
            x1.start()
        else:
            print(" do not start thread 1 because it is still running")

        if not x2.is_alive():
            print(" start thread 2")
            x2 = threading.Thread(target=online_next_departures, args=(station2, direction2))
            x2.start()
        else:
            print(" do not start thread 2 because it is still running")
        count_loops_1 += 1
        print(" - sleep request for ", INTERVALL_request, "s.")
        time.sleep(wait)


def print_timer(wait=INTERVALL_print):
    count_loops = 0
    while True:
        now = datetime.datetime.now()
        worktime_i=0
        if now.hour < WORKTIME_HOURS[worktime_i][0] or now.hour > WORKTIME_HOURS[worktime_i][1]:

            print(" - outside of working ours. sleep for ", wait, "s.")
            print_lcd("                    ", 0)
            print_lcd("   Good Night :)    ", 1)
            print_lcd("                    ", 2)
            print_lcd("                    ", 3)
            time.sleep(wait)
            continue

        print(" ---- begin of print loop (" + str(count_loops) + "). Time: ", datetime.datetime.now(), "----")
        update_lines()
        print(" - sleep for ", INTERVALL_print, "s.")
        time.sleep(wait)
        count_loops += 1


# main script

thread_print = threading.Thread(target=print_timer, args=(INTERVALL_print,))  # every x seconds
thread_requests = threading.Thread(target=request_timer, args=(INTERVALL_request,))  # every y seconds

thread_print.start()
thread_requests.start()
