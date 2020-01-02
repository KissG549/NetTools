from __future__ import print_function

from __future__ import absolute_import

import io, os, sys, time, getopt
import signal, struct
import re # for filter
from cStringIO import StringIO
import string

import general_device
from general_device import *

portlongname1 = "GigabitEthernet2/0/10"
portlongname2 = "GigabitEthernet1/0/9"
portlongname3 = "Vlan115"
portlongname4 = "TenGigabitEthernet10/1/1012"

def get_short_portname( longportname ):

    if len(longportname) < 3:
        return None
    # endif
    short_portname = str()
    short_portname = longportname[0:2]
    postfix = ""

    iterator = 0
    while iterator < len(longportname):
        if str(longportname[:0-iterator]).isalpha():
            # it's the text and not /
            postfix = longportname[0-iterator:]
            break;
        iterator += 1

    short_portname += postfix

    return short_portname


class myClass:
    mynum = 0

class myClass2:
    mynum = 1
    num = 2

myvar = myClass()

print(isinstance(myvar, myClass2))
#print type(myClass)
