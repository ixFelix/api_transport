#!/usr/bin/env python
# coding: utf-8

import api_handler
import sys
import memorizer
import plot
import data_saver
import time
import loop_handler
import tools
import settings
# ----- settings --------

maxNo=6
name0 = ["Tauernallee/Säntisstraße","Alt-Mariendorf Bus"]
freq0 = ["10","6"]
s = settings.get_settings()


# ---- debugging ------
#api_handler.nameToExt("Alt-Mariendorf")

# ----- run --------
loop_handler.add_requests(s)
loop_handler.runLoops()




# ----- plot --------
#plot.nice_nextXDeparturesAt(response)


# ---- old/deprecated -----
#loop_handler.start_loop(name0, maxNo)
	
#response = data_saver.load("stationResponse_20200211214153.c")
#print(type(response))
#plot.plotDict(response)











print("finished :)")
sys.exit()

#command, param ='location.nearbystops', {'originCoordLat':52.50798,'originCoordLong':13.38,'maxNo':2}
#command, param ='departureBoard', {'extId':900070401,'maxNo':1}
command, param ='location.name', {"input":"Tauernallee/Santisstrasse","maxNo":2}
#command, param ='journeyDetail', {"id":"1|25024|8|86|18052019"}

api_handlerresponse = getData(command, param)
#prettyPrint(response)
#print(short_departureAt("Tauernallee/Santisstrasse"))
#prettyPrint(short_departureAt("Zoolo"))