#!/usr/bin/env python
# coding: utf-8
import numpy as np
import api_handler
import data_saver
import time
t0=time.time()
lastRequest=time.time()

requestFrequency = 5*60+10
requestStd = 30
minimumRequestDowntime = 10
loopLength=10 # how often shall each task (frequency) be done?

# different tasks: ----------
requestTypes = []
#requestParams = []
stationNames = []
requestFrequencies = []
requestMaxNos = []

timetable = None
differences = None

def add_requests(s):
	for i in range(len(s["requestTypes"])):
		#add_request(reqTypes[i], requestParams[i], frequencies[i], maxNos[i])
		add_request(s["requestTypes"][i],s["stationNames"][i],s["frequencies"][i],s["maxNo"][i])
def add_request(reqType, stationName, frequency=300, maxNo=6):
	global requestTypes, stationNames, requestFrequencies, requestMaxNos
	requestTypes.append(reqType)
	#requestParams.append(requestParam)
	stationNames.append(stationName)
	requestFrequencies.append(frequency)
	requestMaxNos.append(maxNo)
	print("new:", requestTypes, stationNames, requestFrequencies, requestMaxNos)

def doRequest(task):
	reqType = requestTypes[task]
	global lastRequest
	timeSinceLastRequest = time.time()-lastRequest
	#print("  time timeSinceLastRequest=",timeSinceLastRequest)
	if timeSinceLastRequest<minimumRequestDowntime:
		print("   - delaying request by "+str(minimumRequestDowntime- timeSinceLastRequest)[0:4]+ " sec.")
		time.sleep(minimumRequestDowntime- timeSinceLastRequest)
	if reqType=="departure":
		#print("  pseudo running request type "+str(reqType))
		ret = api_handler.short_departureAt(stationNames[task],requestMaxNos[task])
		pass
	else:
		print(" -- ERROR in loop_handler.doRequest(): I do not know this request Type: "+str(reqType))
	lastRequest = time.time()
	return ret

def prepareLoops():
	global timetable, differences
	numberOfTasks = len(requestFrequencies)
	timetable = np.ndarray((numberOfTasks*loopLength,2))
	for task in range(numberOfTasks):
		timetable[task*loopLength:(task+1)*loopLength,0] = np.array([requestFrequencies[task]*i for i in range(loopLength)])
		timetable[task*loopLength:(task+1)*loopLength,1] = task
	timetable = timetable[np.lexsort((timetable[:,1],timetable[:,0]))]
	print(timetable)
	differences = np.diff(timetable[:,0],axis=0)
	print(differences)

def checkLoopFrequency():
	meanDiff = np.mean(differences)
	if minimumRequestDowntime> meanDiff:
		print("WARNING: frequency is to high. Average frequency:",meanDiff,", minimum downtime between requests: ", minimumRequestDowntime)

def runLoops():
	prepareLoops()
	checkLoopFrequency()
	print("pseudo start loop")
	go=True
	counter=0
	while(go):
		task = int(timetable[counter,1])
		print(str(time.time()-t0)[0:2]," (scheduled:",timetable[counter,0],"): do request ",requestTypes[task], stationNames[task], requestFrequencies[task], requestMaxNos[task])
		
		response = doRequest(task)			
		toSave = {"departure":response}
		data_saver.save(toSave)
		
		currentRuntime = time.time()-t0
		timeTillNextEvent = timetable[counter+1,0]-currentRuntime
		#print("  time till next event:",timeTillNextEvent)
		print(" ",time.ctime()," + ", timeTillNextEvent)
		if timeTillNextEvent>0:
			#print(" sleep for ",timeTillNextEvent)
			time.sleep(timeTillNextEvent)
		counter+=1

def start_loop(name0, maxNo):
	go=True
	while(go):
		response = api_handler.short_departureAt(name0, maxNo)
		toSave = {"departure":response}
		data_saver.save(toSave)
		sleeptime=max(10, requestFrequency + np.random.normal(0,requestStd))
		print("",time.ctime()," + ", sleeptime)
		time.sleep(sleeptime)