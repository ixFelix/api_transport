#!/usr/bin/env python
# coding: utf-8

import requests
import time
#from time import strftime
import datetime
import numpy as np
import re
import xmltodict
import pprint# as pp
#import process_command
#print(dir(process_command))
import memorizer
import tools

def openWebsite(adress, typeX="xlm"):
    r = requests.get(adress)
    if typeX=="xml":
        return r.text
    elif typeX=="json":
        return r.json()

def prettyPrint(text):
    pp = pprint.PrettyPrinter(indent=1)
    pp.pprint(text)

def process_command_vbb(command, param):  
    def furtherParamString(param):#,listToDelete):
        ret=""
        for key in param.keys():
            ret+= "&"+str(key)+"="+str(param[key])
        return ret
    beforeId=command
    behindId=furtherParamString(param)
    return {"beforeId":beforeId, "behindId":behindId}

def createAdress_vbb(command, param):
    # https://3.vbb.transport.rest/stops/900000013102/departures?when=tomorrow%206pm&results=3
    baseurl="http://demo.hafas.de/openapi/vbb-proxy/"
    commands = process_command_vbb(command, param)
    accessId ="felix-fauer-8b71-1705950c2589"
    adress = baseurl + commands['beforeId'] + "?accessId=" + accessId + commands['behindId']
    print("  "+str(adress))
    return adress

def createAdress_bvg_open(command, param):
    # https://2.bvg.transport.rest/stations/900070301/departures/
    def commandsString(command):#,listToDelete):
        ret=""
        for key in command.keys():
            ret+= "/"+str(key)+"/"+str(command[key])
        return ret
    def paramsString(param):#,listToDelete):
        ret=""
        for key in param.keys():
            ret+= "?"+str(key)+"="+str(param[key])
        return ret
    baseurl="https://2.bvg.transport.rest"
    commands = commandsString(command)
    params = paramsString(param)
    adress = baseurl + commands + params
    print("  "+str(adress))
    return adress
    
def responseToDict(response):
    return xmltodict.parse(response)

def getData(command, param, api):
    if api=="vbb":
        response_xml = openWebsite(createAdress_vbb(command, param),typeX="xml")
        response = responseToDict(response_xml)    
    elif api=="bvg_open":
        response = openWebsite(createAdress_bvg_open(command, param),typeX="json")
    #print(response)
    return response
    

def nameToExt(name):
	ext = memorizer.doesItExist(name)
	if ext:
		return ext
	else:
		response = getData('location.name', {"input":name,"maxNo":1}, api="vbb")
		ext = response['LocationList']['StopLocation']['@extId']
		memorizer.addIfNew(name, ext)
		return ext

def short_departureAt(name, maxNo=3, timeShift=-5):
    ext=nameToExt(name)
    depTime = tools.getTime(timeShift, xformat="unix")
    print("supposed time:", depTime)
    #departureTime = str(times["hour"]).zfill(2)+":"+str(times["minute"]).zfill(2)
    command, param ={'stations':ext,'departures':""}, {"when":int(depTime)}
    response = getData(command, param, api="bvg_open")
    #print(response)
    return response

