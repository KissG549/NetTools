
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

__trunk_output = """sw-01>sh int trunk

Port        Mode             Encapsulation  Status        Native vlan
Gi0/1       on               802.1q         trunking      119

Port        Vlans allowed on trunk
Gi0/1       1-4094
Gi1/7       1,100,200-204
Gi1/9       2,5,8,11,21,26,100,109,129,200-204,211-214
Gi1/10      2,5,7-8,11,100,200-204
Gi1/12      2,5,8,11,21,26,100,129,200-204
Gi1/13      2,5,7-8,11,21,26,100,112,129,200-204,211-214
Gi1/14      2,5,8,11,21,26,100,129,200-204
Gi1/15      2,5,8,11,100,200-204
Gi1/16      2,5,7-8,11,100,113,200-204
Gi1/17      2,5,7-8,11,21,26,100,112,129,200-204
Gi1/18      2,5,8,11,100,112,200-204
Gi1/23      20-22,30,50,60,100,200-204
Gi1/24      20-22,30,50,60,100,200-204
Gi2/47      20-22,30,50,60,100,201-204,401-403
Po1         1,3,5,50,100,200-204,211-214,888
Po2         1,3,5,9,21,26,100,129,200-204,211-214,888
Po3         1,4-5,7,21,26,100,129,200-204,211-214
Te1/5/3             6,10,21,26,100,129,132-133,142-143,146-147,153-154,157-158,201,203
Te1/5/14            1-11,20-22,26,50,60,100-113,124-130,132-147,150-159,166-180,182,184,186-189,200-204,211-214,350,401-403,888,900,999-1000
Te2/1/1             100

Port        Vlans allowed and active in management domain
Gi0/1       1,51,99-100,115-121,135,198-201,333,431,616,618-620,666

Port        Vlans in spanning tree forwarding state and not pruned
Gi0/1       1,51,99-100,115-121,135,198-201,333,431,616,618-620,666"""


print ("<process_trunk_output>")

__trunk_output = StringIO(__trunk_output)
interface = DeviceInterface()
port = ""
allowed_vlans = ""
native_vlan = ""
is_native_vlan_section = False
is_allowed_vlan_section = False

while True:
    # Go through line by line
    line = __trunk_output.readline()
    items = line.split()

    if len(line) == 0:
        break

    if (len(items) < 2) : #or (items[0] == 'Port'):
        continue

    print("size: ", len(items))

    if(len(items) > 5) and (items[4] == 'Native'):
        is_allowed_section = False
        is_native_vlan_section = True
        continue
    if(len(items) ==5) and (items[2] == 'allowed'):
        is_allowed_vlan_section = True
        is_native_vlan_section = False
        continue
    if(items[0] == 'Port'):
        is_allowed_vlan_section = False
        is_native_vlan_section = False
        #continue
    if is_native_vlan_section:
        port = items[0]
        if len(items)>3:
            native_vlan = items[4]
        print("Native VLAN: %s - %s" % (port, native_vlan))
        # Save native VLAN and port here
    if is_allowed_vlan_section:
        port = items[0]
        allowed_vlans = items[1]
        print("Allowed VLAN: %s - %s" % (port, allowed_vlans))
        # Save allowed VLANS here


    print(items)



print ("</process_trunk_output>")
