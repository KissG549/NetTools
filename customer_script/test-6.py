from __future__ import print_function

from __future__ import absolute_import

import io, os, sys, time, getopt
import signal, struct
import re # for filter
from cStringIO import StringIO
import string

import general_device
from general_device import *

__vtp_output = """sw7>sh vtp status
VTP Version capable             : 1 to 3
VTP version running             : 2
VTP Domain Name                 : VTP_GU
VTP Pruning Mode                : Disabled
VTP Traps Generation            : Enabled
Device ID                       : 0015.c6bf.1080
Configuration last modified by 1.1.1.1 at 9-27-11 09:22:33

Feature vtp:
--------------
VTP Operating Mode                : Client
Maximum vtps supported locally   : 1005
Number of existing vtps          : 27
Configuration Revision            : 28
MD5 digest                        : 0x3D 0xD4 0x27 0xF2 0xDB 0x71 0xF0 0xB3
                                    0x8A 0xBF 0xC0 0x68 0xDD 0xCA 0x62 0x67
"""

print ("<process_show_vtp_output>")

__vtp_output = StringIO(__vtp_output)

vtp_domain = ""
vtp_mode = ""

VTP_STR = "VTP"
DOMAIN_STR = "Domain"
OPERATING_STR = "Operating"

while True:
    # Go through line by line
    line = __vtp_output.readline()
#    line = line.replace(", ",",")
    #print( line )
    items = line.split()

    # if the line is empty (last line) or LLDP is not enabled, then quit
    if (len(line) == 0):
        break

    if (len(items) < 1) or ("--------------" in line):
        continue

    if items[0] == VTP_STR:

        if (( len(items) == 5) and
            (items[1] == DOMAIN_STR)):

            vtp_domain = items[4].strip()
        elif (( len(items) == 5) and
            (items[1] == OPERATING_STR)):

            vtp_mode = items[4].strip()
    #endif

print(vtp_domain)
print(vtp_mode)
print ("</process_show_vtp_output>")
