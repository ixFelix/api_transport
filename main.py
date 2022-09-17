import requests
import time
#from time import strftime
import datetime
import numpy as np

def openWebsite(adress):
    r = requests.get(adress)
    return r.text


def createCommand(command,param):
    if command=="locationNearbystops":
        ret = command_locationNearbystops(param)
    #elif:
    else:
        print("Error in createCommand: command not known!")
    return ret

    def command_locationNearbystops(param):
        lon, lat, maxNo = param['lon'], param['lat'], param['maxNo']
        beforeId="location.nearbystops"
        behindId="originCoordLong="+str(lon)+"&originCoordLat="+str(lat)+"&maxNo="+str(maxNo)
        return {"beforeId":beforeId, "behindId":behindId}


def createAdress(command, param):
    baseurl="http://demo.hafas.de/openapi/vbb-proxy/"
    command = createCommand(command, param)
    accessId ="felix-fauer-8b71-1705950c2589"
    adress=baseurl+command['beforeId']+"?accessId="+accessId+"&"+command['behindId']
    print(adress)
    return adress


#print(openWebsite("http://demo.hafas.de/openapi/vbb-proxy/location.nearbystops?accessId=felix-fauer-8b71-1705950c2589&originCoordLong=13.380000&originCoordLat=52.5079800&maxNo=2"))
command='locationNearbystops'
param={'lat':52.50798,'lon':13.38,'maxNo':1}
print(openWebsite(createAdress(command, param)))

