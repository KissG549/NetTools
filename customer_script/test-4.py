
from __future__ import print_function

from __future__ import absolute_import

import io, os, sys, time, getopt
import signal, struct
import re # for filter
from cStringIO import StringIO
import string

import general_device
from general_device import SwitchClass
from general_device import DeviceInterface

__cdp_output = """sw-02>sh cdp neighbors
Capability Codes: R - Router, T - Trans Bridge, B - Source Route Bridge
                  S - Switch, H - Host, I - IGMP, r - Repeater, P - Phone,
                  D - Remote, C - CVTA, M - Two-port Mac Relay

Device ID        Local Intrfce     Holdtme    Capability  Platform  Port ID
sw-03
                 Fas 0/46          168             T B I  AIR-CAP17 Gig 0.1
sw-04
                 Fas 0/47          176             T B I  AIR-CAP17 Gig 0.1
sw-05
                 Gig 0/3           130              S I   WS-C3750X Gig 1/0/23
"""

print ("<process_lldp_output>")

__cdp_output = StringIO(__cdp_output)
interface = DeviceInterface()
localport = ""
remoteport = ""
neighbor = ""
neighbor_section = False
DEVICE_ID_CHARS = 16
LOCAL_INT_CHARS = 18
HOLDTIME_CHARS = 11
CAPABILITY_CHARS = 10
PLATFORM_CHARS = 10
PORT_ID_CHARS = 8
REMOTE_PORT_CHARS = 68
while True:
    # Go through line by line
    line = __cdp_output.readline()
    items = line.split()

    # if the line is empty (last line) or LLDP is not enabled, then quit
    if (len(line) == 0) or ("not enabled" in line):
        break

    if (len(items) < 1):
        continue

    if items[0] == "Device":
        neighbor_section = True

    if (len(items)==1) and neighbor_section:
        # There is only the device ID
        neighbor = items[0].split(".")
        neighbor = neighbor[0].strip()
        #print("neigh: ",neighbor)
    elif (len(items)>6) and neighbor_section:
        if(len(line[0:DEVICE_ID_CHARS].strip()) != 0 ):
            # Dev id is not empty
            neighbor = line[0:DEVICE_ID_CHARS].strip()
        # END if
        localport = line[DEVICE_ID_CHARS:DEVICE_ID_CHARS+LOCAL_INT_CHARS].strip()
        localport = localport.replace(" ", "")
        localport = localport[:2] + localport[3:]
        remoteport = line[(REMOTE_PORT_CHARS):].strip()
        remoteport = remoteport.replace(" ", "")
        remoteport = remoteport[:2] + remoteport[3:]

        # Save parameters here
        print("size: ", len(items))
        print("neighbor: ", neighbor)
        print("localport: ", localport)
        print("remoteport: ", remoteport)

    #print(line)

# END while loop

print ("</process_lldp_output>")
