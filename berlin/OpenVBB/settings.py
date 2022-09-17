#!/usr/bin/env python
# coding: utf-8

requestTypes = ["departure"					,"departure"]
stationNames = ["Tauernallee/Säntisstraße"	,"U Alt-Mariendorf (Berlin)"]
frequencies =  [9.3*60						,9*60]# [7,3]#
maxNo =        [9							,19]# [6,10]# # not needed in open api (default: next 10 min)
timeShift =    [-5                          ,-5]



def get_settings():
	ret =  {"maxNo":maxNo,
			"stationNames":stationNames,
			"frequencies":frequencies,
			"requestTypes":requestTypes,
			"timeShift":timeShift
	}
	return ret