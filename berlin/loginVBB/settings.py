#!/usr/bin/env python
# coding: utf-8

requestTypes = ["departure"					,"departure"]
stationNames = ["Tauernallee/Säntisstraße"	,"U Alt-Mariendorf (Berlin)"]
frequencies =  [9.3*60						,9*60]# [7,3]#
maxNo =        [9							,19]# [6,10]#




def get_settings():
	ret =  {"maxNo":maxNo,
			"stationNames":stationNames,
			"frequencies":frequencies,
			"requestTypes":requestTypes
	}
	return ret