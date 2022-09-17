#!/usr/bin/env python
# coding: utf-8

import pickle
import time
import tools

savePath="data_storage/stationResponse/"
standardPrefix = "stationResponse"
standartPostfix = ".c"
def save(obj, filename=None, printIt=True):
	if filename==None:
		filename = standardPrefix
	#times = time.ctime().split()
	#timesMill = time.time()
	#milliString = str(timesMill).split(".")[1]#-int(timesMill))
	prefix = filename
	postfix = standartPostfix
	timeString = tools.getMilliTimeString()
	finalFileName = prefix +"_"+ timeString + postfix

	tools.save(obj, savePath+finalFileName, printIt=printIt)
	
def load(filename): # either "20200211214153" or "stationResponse_20200211214153.c"
	if filename[-2:] != ".c":
		filename = standardPrefix +"_"+ filename + standartPostfix
	ret=tools.load(savePath+filename)
	return ret