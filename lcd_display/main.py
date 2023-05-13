import requests, json
import time
import datetime
import numpy as np
import xmltodict

use_lcd = True # for debugging. False on pc, true on raspberry

if use_lcd:
    import lcddriver

    lcd = lcddriver.lcd()

# debug. To undebug, remove all ## before lcd

t1 = time.time()
INTERVALL = 30
INTERVAL_owm = 60 * 10  # 10 min temporal resolution of model
WORKTIME_HOURS = [[7, 23]]

# baseurl = "https://v6.vbb.transport.rest/"
baseurl = "https://v5.vbb.transport.rest/"
urlending = "&accept=application/x-ndjson"


def responseToDict(response, return_json=True):
    if return_json:
        return json.loads(response)
    else:
        return xmltodict.parse(response)


def openWebsite(address):
    # print("    - start api request")
    print(address)
    try:
        r = requests.get(address)
    except requests.exceptions.MissingSchema as e:
        print(" - Error in Request (Missing  Schema):", e)
        # print("    - received answer", time.time() - t1)
    except requests.exceptions.ConnectionError as e:
        print(" - Error in Request (ConnectionError. Does page exist?):", e)
    else:
        # print(r.text)
        return r.text


# print(openWebsite("https://www.asfegoogle.de"))


def api_vbb(command, param={}):
    def furtherParamString(param):  # ,listToDelete):
        ret = ""
        for key in param.keys():
            ret += "&" + str(key) + "=" + str(param[key])
        return ret

    def process_command_vbb(command, param):
        beforeId = command
        behindId = furtherParamString(param)
        return {"beforeId": beforeId, "behindId": behindId}

    def vbb_createAdress(command, param):
        commands = process_command_vbb(command, param)
        # accessId ="felix-fauer-8b71-1705950c2589"
        address = baseurl + commands['beforeId'] + "/" + commands['behindId'] + "&accept=application/x-ndjson"
        # print(address)
        return address

    response_xml = openWebsite(vbb_createAdress(command, param))
    if response_xml is None:
        print("Warning: response is empty (None).")
        return ""
    if len(response_xml) == 0:
        print("Warning: response is empty (len 0).")
        return ""
    else:
        return responseToDict(response_xml)


last_request = ""


def api_owm(check_interval=True):
    # openweathermap
    # if old is given, check interval
    global last_request
    if check_interval and isinstance(last_request, datetime.date):
        now = datetime.datetime.now()
        time_since_last_request = (now - last_request).seconds  # in minutes
        if time_since_last_request < INTERVAL_owm:
            print("wait until", INTERVAL_owm / 60, "min have passed. (Currently", time_since_last_request / 60, ")")
            return "stalling"
        else:
            print(INTERVAL_owm / 60, "minutes have passed. Continue weather request.")
    else:
        print("Either check_interval is not requested or this is the first request. Continue weather request.")

        # check interval and return old, if necessary

    # else continue:
    url = "http://api.openweathermap.org/data/2.5/forecast?lat=52.4385&lon=13.3927&units=metric&appid" \
          "=09638815cd6e1c6a51e023f776f021ce"
    response = openWebsite(url)
    last_request = datetime.datetime.now()

    if len(response) > 0:
        return responseToDict(response)
    else:
        print("Warning: response is empty.")
        return ""


def nameToExtStation(name):
    response = api_vbb('locations?', {"query": name, "maxNo": 1, "poi": "false", "addresses": "false"})
    id = response[0]['location']['id']
    name_found = response[0]['name']
    print("Name:", name, ". Name found:", name_found, ". ID:", id)
    return id  # ['@extId']


def nextDeparturesAtStop(name=False, ext=0, ext_dir="", maxNo=3, duration=10):
    if not ext:
        if name:
            ext = nameToExtStation(name)
        else:
            print("ERROR. You must provide name or ext.")

    command, param = 'stops/' + str(ext) + '/' + 'departures?', \
                     {'direction': ext_dir, 'results': maxNo, 'duration': duration}
    response = api_vbb(command, param)
    return response


ext = 900070401  # "Tauernallee Santisstrasse"
ext_dir = 900070301  # U Alt-Mariendorf
ext_dir2 = 900000082202  # Johannisthaler Chaussee

i = 0
# weather = "not requested"

while True:
    # for i in range(100):
    # print("  - begin of loop ("+str(i)+"). Time: ", time.time() - t1)
    t_loop = time.time()
    now = datetime.datetime.now()

    # check for working hours. otherwise sleep for one intervall.
    go = False
    for worktime_i in range(len(WORKTIME_HOURS)):
        if now.hour >= WORKTIME_HOURS[worktime_i][0] and now.hour < WORKTIME_HOURS[worktime_i][1]:
            go = True
    if not go:
        print("no working hours. sleep for ", INTERVALL, "s.")
        if use_lcd:
            lcd.lcd_clear()
            lcd.lcd_display_string("Good Night :)", 1)
        time.sleep(INTERVALL)
        continue

    nextDep = nextDeparturesAtStop(ext=900070401, ext_dir=ext_dir, maxNo=6, duration=20)  # all bus to Mariendorf
    nextDep2 = nextDeparturesAtStop(ext=900070401, ext_dir=ext_dir2, maxNo=2, duration=40)  # X71 to Gropius
    # nextDep = ""
    weather = api_owm(check_interval=True)

    # -------- handle lines 1,2,3 (departures) --------
    print("Handle lines 1,2,3 (departures")
    if len(nextDep) > 0:
        # print("  - end of loop. Loop runtime =", time.time() - t_loop)

        print("now: ", now)
        print("handle next 2 departures and display long")

        def extract_from_departures(nextDep_i):
            iLine = nextDep_i['line']['name']
            iDest = nextDep_i['direction'][0:12]
            iTime = nextDep_i['when']
            iWait = datetime.datetime.strptime(iTime[0:19],
                                               '%Y-%m-%dT%H:%M:%S') - now
            if iWait.seconds > 24 * 60 * 60 / 2:
                diffMin = (24 * 60 * 60 - iWait.seconds) // 60
            else:
                diffMin = iWait.seconds // 60
            return {"iLine": iLine, "iDest": iDest, "diffMin": diffMin}

        for i in range(min(2, len(nextDep))):
            extracted = extract_from_departures(nextDep[i])
            iLine, iDest, diffMin = extracted["iLine"], extracted["iDest"], extracted["diffMin"]
            final_str = iLine.ljust(3) + " " + iDest.ljust(11) + " " + str(diffMin).rjust(2) + "'"
            print(" lcd line " + str(i) + ": " + final_str + " (len:" + str(len(final_str)) + ")")

            # send string to lcd display
            if use_lcd:
                print("send to lcd...")
                lcd.lcd_display_string(final_str, i + 1)
        print("handle line 3 (2 more departures to Mariendorf and one to Gropius) and display short")
        extracted2 = [extract_from_departures(nextDep[i]) for i in (3, 4)]
        iLine, diffMin = extracted2[0]["iLine"], extracted2[0]["diffMin"]
        iLine2, diffMin2 = extracted2[1]["iLine"], extracted2[1]["diffMin"]
        extracted_x71 = extract_from_departures(nextDep2[0])
        diffMin_x71 = extracted_x71["diffMin"]
        final_str = iLine[0]+":"+str(diffMin)+", "+iLine2[0]+":"+str(diffMin2)+", X71*:"+str(diffMin_x71)+""
        print(" lcd line 3: " + final_str + " (len:" + str(len(final_str)) + ")")
        if use_lcd:
            print("send to lcd...")
            lcd.lcd_display_string(final_str, 3)
    else:
        final_str = "no response (vbb)"
        print(" lcd line 1,2,3:", final_str)
        if use_lcd:
            print("send to lcd...")
            [lcd.lcd_display_string(final_str, i + 1) for i in range(3)]

    # handle third line (weather)
    print("handle line 4 (weather)")
    if len(weather) == 0:
        final_str = "no response (owm)"
        print(" lcd line 4: " + final_str + " (len:" + str(len(final_str)) + ")")
    elif weather == "stalling":
        print("stalling in writing process.")
    else:
        # 3 hour time steps (max 8 per day)
        n_timeSteps = len(weather['list'])
        epochs = [weather['list'][i]['dt'] for i in range(n_timeSteps)]
        datetime_dayOfMonth = [datetime.datetime.fromtimestamp(epochs[i]).day for i in range(n_timeSteps)]
        if now.hour < 20:
            dayDelay = 0
        else:
            dayDelay = 1
        idxs = np.where(np.array(datetime_dayOfMonth) == now.day + dayDelay)[0]
        temp_dayMax = max([weather['list'][i]["main"]["temp_max"] for i in idxs])
        temp_next = weather['list'][0]["main"]["temp_max"]
        pop_dayMax = max([weather['list'][i]["pop"] for i in idxs])
        wind_dayMax = max([weather['list'][i]["wind"]["gust"] for i in idxs])
        final_str = "T:" + str(round(temp_next)) + "-" + str(round(temp_dayMax)) + ", pr:" + str(
            round(pop_dayMax * 100)) + "" + ", w:"+str(round(wind_dayMax))+\
            ("*" if dayDelay == 1 else "")
        final_str2 = "T: " + str(round(temp_next)) + ", Tx:" + str(round(temp_dayMax)) + ", pr:" + str(
            round(pop_dayMax * 10)) + "%" + ", w:" + str(round(wind_dayMax)) + \
                    ("*" if dayDelay == 1 else "")
        print(" lcd line 4: " + final_str + " (len:" + str(len(final_str)) + ")")
        if use_lcd:
            lcd.lcd_display_string(final_str, 4)

    print("sleep for", INTERVALL, "s.")
    time.sleep(INTERVALL)
    i = i + 1

print("end of script. Total runtime =", time.time() - t1)
