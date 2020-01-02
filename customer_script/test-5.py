
from __future__ import print_function

from __future__ import absolute_import

import io, os, sys, time, getopt
import signal, struct
import re # for filter
from cStringIO import StringIO
import string

from general_device import *

__vlan_output = """sw-06>sh vlan brief

VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Gi0/2, Gi0/3, Gi0/4
51   PIPELINE               active
99   VLAN0099                         active
100  NULL                             active
115  TEST_PXE                         active
116  VLAN116               active    Fa0/47, Fa0/48
117  ILO                              active
118  UG                               active    Fa0/3
119  GAD                           active    Fa0/1, Fa0/2, Fa0/4, Fa0/5, Fa0/6, Fa0/7, Fa0/8, Fa0/9, Fa0/10, Fa0/11, Fa0/12, Fa0/13, Fa0/14, Fa0/15, Fa0/16, Fa0/17, Fa0/18, Fa0/19, Fa0/20, Fa0/21, Fa0/22, Fa0/23, Fa0/24, Fa0/25
                                                Fa0/26, Fa0/27, Fa0/28, Fa0/29, Fa0/30, Fa0/31, Fa0/32, Fa0/33, Fa0/34, Fa0/35, Fa0/36, Fa0/37, Fa0/38, Fa0/39, Fa0/40, Fa0/41, Fa0/42, Fa0/43, Fa0/44, Fa0/45, Fa0/46
120  SRV                              active
121  WLAN                             active
135  WLAN135                          active
198  FW2                              active
199  FW1                              active
200  VLAN0200                         active
201  VLAN0201                         active
333  RMT                              active
431  VLAN0431                         active
616  PH1                              active
618  PH2                              active
619  PH3                              active    Fa0/1, Fa0/2, Fa0/4, Fa0/5, Fa0/6, Fa0/7, Fa0/8, Fa0/9, Fa0/10, Fa0/11, Fa0/12, Fa0/13, Fa0/14, Fa0/15, Fa0/16, Fa0/17, Fa0/18, Fa0/19, Fa0/21, Fa0/22, Fa0/23, Fa0/24, Fa0/25, Fa0/26
                                                Fa0/27, Fa0/28, Fa0/30, Fa0/31, Fa0/32, Fa0/33, Fa0/34, Fa0/35, Fa0/36, Fa0/37, Fa0/38, Fa0/39, Fa0/40, Fa0/41, Fa0/42, Fa0/43, Fa0/44, Fa0/45, Fa0/46
620  PH4                              active
666  RMT                              active
1002 fddi-default                     act/unsup
1003 trcrf-default                    act/unsup
1004 fddinet-default                  act/unsup
1005 trbrf-default                    act/unsup
sw-06>

"""

print ("<process_show_vlan_output>")

__vlan_output = StringIO(__vlan_output)
vlan_list = [] # VlanClass - number and name
ports_per_vlan = [] # two dimension list

vlan_section = False
VLAN_ID_CHARS = 5
VLAN_NAME_CHARS = 33
VLAN_STATUS_CHARS = 10
PORT_CHARS = 48

vlan_item = VlanClass()
port = ""

tmp_device = GeneralDevice()

while True:
    # Go through line by line
    line = __vlan_output.readline()
    line = line.replace(", ",",")
    #print( "----->", line )
    items = line.split()

    # if the line is empty (last line) or LLDP is not enabled, then quit
    if (len(line) == 0) or ("Ambiguous" in line):
        break

    if (len(items) < 1) or ("---------" in line):
        continue

    if items[0] == "VLAN":
        vlan_section = True
        continue

    #print("Len: " , len(items))
    # print("itemsitemsitemsitemsitemsitemsitemsitems")
    # print("V_Items: ", items )
    # print("itemsitemsitemsitemsitemsitemsitemsitems")

    ### Process the output
    # IF we are in the vlan section and have enough items to work with
    # If this line is about VLANID, VLAN-description, VLAN-status and assigned ports then
    if (str(items[0]).isdigit() and
        (vlan_section) and
        (str(items[2] == "active")) and
        len(items)>2):

        if vlan_item.number != None:
            # save vlan item to the list
            vlan_list.append(vlan_item)
            # save port's to the list
            ports_per_vlan.append(port)
        # endif

        vlan_item = VlanClass()
        vlan_item.number = items[0].strip()
        vlan_item.name = items[1].strip()
        vlan_item.state = items[2].strip()
        port = items[3].strip()
        # endelse
    elif len(items) == 1:
        # else it must contain only ports for the prev vlan
        port += ","
        port += items[0].strip()
    # endif
# endwhile
# Last line must be added also to the list
# save vlan item to the list
vlan_list.append(vlan_item)
# save port's to the list
ports_per_vlan.append(port)

# print("vlanvlanvlanvlanvlanvlanvlanvlan")
# print(vlan_item.name)
# print(vlan_item.number)
# print("vlanvlanvlanvlanvlanvlanvlanvlan")

# print(ports_per_vlan)
# go through in vlan list with
vlan_iterator = 0
while( vlan_iterator != len(vlan_list)):
#print("VLAN-number: ", vlan_list[iterator].number)
#print("VLAN-name: ", vlan_list[iterator].name)
#print("Port:", ports_per_vlan[iterator])

#print("-------")

#go through the ports
    __ports_loc = ports_per_vlan[vlan_iterator].split(",")
    # print("Ports are:", __ports_loc)
    ports_loc_iterator = 0
    while ports_loc_iterator != len(__ports_loc):

        port_iterator = 0
        while port_iterator != len(tmp_device.ports):
            #print("####>%s<#-#>%s<#" % (tmp_device.ports[port_iterator].interfacename,__ports_loc[ports_loc_iterator] ))
            if tmp_device.ports[port_iterator].interfacename == __ports_loc[ports_loc_iterator]:


                if tmp_device.ports[port_iterator].accessvlan == None:
                    tmp_device.ports[port_iterator].accessvlan = vlan_list[vlan_iterator].number
                    # if it is, then set the current vlan as access vlan
                elif tmp_device.ports[port_iterator].accessvlan != vlan_list[vlan_iterator].number:
                    # if not then set up as voice vlan
                    tmp_device.ports[port_iterator].voicevlan = vlan_list[vlan_iterator].number

            # check vlan is empty or None
            # print("VLAN: ", vlan_list[vlan_iterator].number)
            # print("ACCESS-VLAN: ", tmp_device.ports[port_iterator].accessvlan)
            # print("VOICE-VLAN: ", tmp_device.ports[port_iterator].voicevlan)
                break
            port_iterator+=1

        #end while
        ports_loc_iterator+=1
    #endwhile
    vlan_iterator +=1


print ("</process_show_vlan_output>")
