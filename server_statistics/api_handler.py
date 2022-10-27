import requests, json
import xmltodict

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


def nextDeparturesAtStop(name=False, ext=0, maxNo=3, ext_dir=0):
    if not ext:
        if name:
            ext = nameToExtStation(name)
        else:
            print("ERROR. You must provide name or ext.")

    command = 'stops/' + str(ext) + '/' + 'departures?'
    if ext_dir:
        param = {'direction': ext_dir, 'results': maxNo, 'duration': 20}
    else:
        param = {'results': maxNo, 'duration': 20}
    response = getData(command, param)
    return response


ext = 900070401  # "Tauernallee Santisstrasse"
ext_dir = 900070301  # U Alt-Mariendorf

def handler_debug(ext=ext, maxNo=10, ext_dir=ext_dir):
    # if api is down, use this artificial data for debugging
    return [{'line': {'name': 'M76'},
             'direction': 'Walter-Schreiber-Platz',
             'when': '2022-10-26T23:20:00'}
            for i in range(maxNo)]