#!/usr/bin/env python
# coding: utf-8
import time
import pickle
import datetime
from dateutil.relativedelta import relativedelta	


months={"Jan":"01","Feb":"02","Mar":"03","Apr":"04","Mai":"05","Jun":"06","Jul":"07","Aug":"08","Sep":"09","Oct":"10","Nov":"11","Dez":"12"}
monthsNr={"Jan":1,"Feb":2,"Mar":3,"Apr":4,"Mai":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dez":12}
weekdaysNr={"Mon":0,"Tue":1,"Wed":2,"Thu":3,"Fri":4,"Sat":5,"Sun":6}

def getMilliTimeString(add_millisec=True):
	times = time.ctime().split()
	timesMill = time.time()
	milliString = str(timesMill).split(".")[1]#-int(timesMill))
	finalFileName = times[4] + months[times[1]] + times[2] + times[3][0:2] + times[3][3:5] + times[3][6:8] 
	if add_millisec:
		finalFileName += "_"+ milliString
	return finalFileName

def save(obj, filePathName, printIt=False):
	if printIt:
		print("  saving "+filePathName)
	with open(filePathName, 'wb') as f:
		pickle.dump(obj, f)

def load(filePathName, printIt=False):
	if printIt:
		print("  open "+filePathName)
	with open(filePathName, 'rb') as f:
		load = pickle.load(f)
	return load

def getTime(addMinute, xformat="hourMin"):
	now = datetime.datetime.now()
	add = relativedelta(minutes=addMinute)
	newTime = now + add
	ret = "typeNotSupported"
	if xformat=="hourMin":
		ret = str(newTime.hour)+":"+str(newTime.minute)
	else:
		print("ERROR in tools.getTime(): format not supported: "+str(xformat))
	return ret


#  ------ deprecated ------

"""def getTimeAsDict():
	times = time.ctime().split()
	clock = times[3].split(":")
	myDict = {"weekday":times[0],"weekdayNr":weekdaysNr[times[0]],
		"monthName":times[1],"month":monthsNr[times[1]], "day":times[2],
		"hour":clock[0], "minute":clock[1], "second:":clock[2], 
		"year":times[4]}
	return myDict
"""
