import requests, json
import time
import datetime
import numpy as np
import xmltodict
import lcddriver

t1 = time.time()
INTERVALL = 60
WORKTIME_HOURS = [[7, 10],[19,21]]

baseurl = "https://v5.vbb.transport.rest/"
urlending = "&accept=application/x-ndjson"


def openWebsite(address):
    # print("    - start api request")
    print(address)
    r = requests.get(address)
    # print("    - received answer", time.time() - t1)
    return r.text


def process_command_vbb(command, param):
    def furtherParamString(param):  # ,listToDelete):
        ret = ""
        for key in param.keys():
            ret += "&" + str(key) + "=" + str(param[key])
        return ret

    beforeId = command
    behindId = furtherParamString(param)
    return {"beforeId": beforeId, "behindId": behindId}


def createAdress_vbb(command, param):
    commands = process_command_vbb(command, param)
    # accessId ="felix-fauer-8b71-1705950c2589"
    address = baseurl + commands['beforeId'] + "/" + commands['behindId'] + "&accept=application/x-ndjson"
    #print(address)
    return address


def responseToDict(response, return_json=True):
    if return_json:
        return json.loads(response)
    else:
        return xmltodict.parse(response)


def getData(command, param={}):
    response_xml = openWebsite(createAdress_vbb(command, param))
    return responseToDict(response_xml)


def nameToExtStation(name):
    response = getData('locations?', {"query": name, "maxNo": 1, "poi": "false", "addresses": "false"})
    id = response[0]['location']['id']
    name_found = response[0]['name']
    print("Name:", name, ". Name found:", name_found, ". ID:", id)
    return id  # ['@extId']


def nextDeparturesAtStop(name=False, ext=0, maxNo=3):
    if not ext:
        if name:
            ext = nameToExtStation(name)
        else:
            print("ERROR. You must provide name or ext.")

    command, param = 'stops/' + str(ext) + '/' + 'departures?', \
                     {'direction': ext_dir, 'results': maxNo, 'duration': 20}
    response = getData(command, param)
    return response


ext = 900070401  # "Tauernallee Santisstrasse"
ext_dir = 900070301  # U Alt-Mariendorf

lcd = lcddriver.lcd()


i=0
while True:
#for i in range(100):
    # print("  - begin of loop ("+str(i)+"). Time: ", time.time() - t1)
    t_loop = time.time()
    now = datetime.datetime.now()

    # chech for working hours. otherwise sleep for one intervall.
    go=False
    for worktime_i in range(len(WORKTIME_HOURS)):
        if now.hour >= WORKTIME_HOURS[worktime_i][0] and now.hour < WORKTIME_HOURS[worktime_i][1]:
            go=True
    if not go:
        print("no working hours. sleep for ", INTERVALL, "s.")
        lcd.lcd_clear()
        time.sleep(INTERVALL)
        continue

    try:
        nextDep = nextDeparturesAtStop(ext=900070401, maxNo=4)
        # print("  - end of loop. Loop runtime =", time.time() - t_loop)

        print("now: ", now)
        for i in range(min(4,len(nextDep))):
            iLine = nextDep[i]['line']['name']
            iDest = nextDep[i]['direction'][0:12]
            iTime = nextDep[i]['when']
            iWait = datetime.datetime.strptime(iTime[0:19],
                                               '%Y-%m-%dT%H:%M:%S') - now
            if iWait.seconds > 24 * 60 * 60 / 2:
                diffMin = (24 * 60 * 60 - iWait.seconds) // 60
            else:
                diffMin = iWait.seconds // 60

            final_str = iLine.ljust(3) + " " + iDest.ljust(11) + " " + str(diffMin).rjust(2) + "'"
            print(final_str)

            # send string to lcd display
            print("send to lcd...")
            lcd.lcd_display_string(final_str, i+1)

    except Exception as e:
        print(" - Error in Request:", e)
    print("sleep for",INTERVALL, "s.")
    time.sleep(INTERVALL)
    i=i+1

print("end of script. Total runtime =", time.time() - t1)
