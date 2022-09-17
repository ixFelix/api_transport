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

def openWebsite(adress):
    r = requests.get(adress)
    return r.text

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
    baseurl="http://demo.hafas.de/openapi/vbb-proxy/"
    commands = process_command_vbb(command, param)
    accessId ="felix-fauer-8b71-1705950c2589"
    adress = baseurl + commands['beforeId'] + "?accessId=" + accessId + commands['behindId']
    print("  "+str(adress))
    return adress

#print("https://3.vbb.transport.rest/stops/900000013102/departures?when=tomorrow%206pm&results=3")

def responseToDict(response):
    return xmltodict.parse(response)

def getData(command, param):
    response_xml = openWebsite(createAdress_vbb(command, param))
    #print(response_xml)
    return responseToDict(response_xml)    

def nameToExt(name):
	ext = memorizer.doesItExist(name)
	if ext:
		return ext
	else:
		response = getData('location.name', {"input":name,"maxNo":1})
		#print(response) #del 
		#stopit()		#del
		ext = response['LocationList']['StopLocation']['@extId']
		memorizer.addIfNew(name, ext)
		return ext

def short_departureAt(name, maxNo=3):
    ext=nameToExt(name)
    depTime = tools.getTime(-20, xformat="hourMin")
    #departureTime = str(times["hour"]).zfill(2)+":"+str(times["minute"]).zfill(2)
    command, param ='departureBoard', {'extId':ext,'maxJourneys':maxNo,'time':depTime}
    response = getData(command, param)
    return response

