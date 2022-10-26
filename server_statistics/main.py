import time
import datetime
import numpy as np
import api_handler

t1 = time.time()

ext = 900070401  # "Tauernallee Santisstrasse"
ext_dir = 900070301  # U Alt-Mariendorf


def handler_debug(ext=ext, maxNo=10, ext_dir=ext_dir):
    return [{'line': {'name': 'M76'},
             'direction': 'Walter-Schreiber-Platz',
             'when': '2022-10-26T23:20:00'}
            for i in range(maxNo)]


for i in range(100):
    # print("  - begin of loop ("+str(i)+"). Time: ", time.time() - t1)
    t_loop = time.time()

    try:
        #nextDep = api_handler.nextDeparturesAtStop(ext=ext, maxNo=10, ext_dir=ext_dir)
        nextDep = handler_debug(ext=ext, maxNo=10, ext_dir=ext_dir)
        # print("  - end of loop. Loop runtime =", time.time() - t_loop)

        now = datetime.datetime.now()
        # print("now: ", now)
        for i in range(len(nextDep)):
            iLine = nextDep[i]['line']['name']
            iDest = nextDep[i]['direction'][0:12]
            iTime = nextDep[i]['when']
            iWait = datetime.datetime.strptime(iTime[0:19],
                                               '%Y-%m-%dT%H:%M:%S') - now
            if iWait.seconds > 24 * 60 * 60 / 2:
                diffMin = (24 * 60 * 60 - iWait.seconds) // 60
            else:
                diffMin = iWait.seconds // 60

            #final_str = iLine.ljust(3) + " " + iDest.ljust(11) + " " + str(diffMin).rjust(2) + "'"
            #print(final_str)


    except Exception as e:
        print(" - Error in Request:", e)
    time.sleep(5 * 60)

print("end of script. Total runtime =", time.time() - t1)
