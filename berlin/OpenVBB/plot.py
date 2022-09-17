#!/usr/bin/env python
# coding: utf-8

import pprint

def nice_nextXDeparturesAt(response):
    print("Next departures at "+str(response['DepartureBoard']['Departure'][0]['@stop'])+":\n")
    print("   Line        Destination                     Time                  (intern data)")
    print("   ----        -----------                     ----")
    for dep in response['DepartureBoard']['Departure']:
        if "@rtTime" in dep.keys():
            if dep['@time'][0:5]!= dep['@rtTime'][0:5]:
                print("   "+dep['@name'].lstrip().ljust(8)+"    "+dep['@direction'].ljust(30)[0:30]+"  "+
                      dep['@time'][0:5]+" ("+dep['@rtTime'][0:5]+")"+"".ljust(9)+dep['JourneyDetailRef']['@ref'])
            else: 
                print("   "+dep['@name'].lstrip().ljust(8)+"    "+dep['@direction'].ljust(30)[0:30]+"  "+
                      dep['@rtTime'][0:5]+"       "+"".ljust(10)+dep['JourneyDetailRef']['@ref'])
        else:
            print("   "+dep['@name'].lstrip().ljust(8)+"    "+dep['@direction'].ljust(30)[0:30]+"  "+
                  dep['@time'][0:5]+" (?)    "+"".ljust(9)+dep['JourneyDetailRef']['@ref'])

def plotDict(text):
  #print(type(text))
	pp = pprint.PrettyPrinter(indent=1)
	pp.pprint(text)
