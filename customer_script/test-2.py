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

__interface_output = """sw-01>show int status
 show int status

 Port      Name               Status       Vlan       Duplex  Speed Type
 Fa0/1                        notconnect   119          auto   auto 10/100BaseTX
 Fa0/2                        connected    119        a-full  a-100 10/100BaseTX
 Fa0/3                        connected    118        a-full  a-100 10/100BaseTX
 Fa0/4                        notconnect   119          auto   auto 10/100BaseTX
 Fa0/5                        connected    119        a-full  a-100 10/100BaseTX
 Fa0/6                        notconnect   119          auto   auto 10/100BaseTX
 Fa0/7                        notconnect   119          auto   auto 10/100BaseTX
 Fa0/8                        notconnect   119          auto   auto 10/100BaseTX
 Fa0/9                        notconnect   119          auto   auto 10/100BaseTX
 Fa0/10                       notconnect   119          auto   auto 10/100BaseTX
 Fa0/11                       notconnect   119          auto   auto 10/100BaseTX
 Fa0/12                       notconnect   119          auto   auto 10/100BaseTX
 Fa0/13                       connected    119        a-full  a-100 10/100BaseTX
 Fa0/14                       notconnect   119          auto   auto 10/100BaseTX
 Fa0/15                       notconnect   119          auto   auto 10/100BaseTX
 Fa0/16                       notconnect   119          auto   auto 10/100BaseTX
 Fa0/17                       notconnect   119          auto   auto 10/100BaseTX
 Fa0/18                       notconnect   119          auto   auto 10/100BaseTX
 Fa0/19                       notconnect   119          auto   auto 10/100BaseTX
 Fa0/20                       connected    119        a-full  a-100 10/100BaseTX
 Fa0/21                       connected    119        a-full  a-100 10/100BaseTX
 Fa0/22                       connected    119        a-full  a-100 10/100BaseTX
 Fa0/23                       notconnect   119          auto   auto 10/100BaseTX
 Fa0/24                       connected    119        a-full  a-100 10/100BaseTX
 Fa0/25                       connected    119        a-full  a-100 10/100BaseTX
 Fa0/26    Port disabled -    disabled     119          auto   auto 10/100BaseTX
 Fa0/27                       notconnect   119          auto   auto 10/100BaseTX
 Fa0/28                       connected    119        a-full  a-100 10/100BaseTX
 Fa0/29                       connected    119        a-full  a-100 10/100BaseTX
 Fa0/30                       notconnect   119          auto   auto 10/100BaseTX
 Fa0/31                       connected    119        a-full  a-100 10/100BaseTX
 Fa0/32                       connected    119        a-full  a-100 10/100BaseTX
 Fa0/33                       err-disabled 119          auto   auto 10/100BaseTX
 Fa0/34                       notconnect   119          auto   auto 10/100BaseTX
 Fa0/35                       connected    119        a-full   a-10 10/100BaseTX
 Fa0/36                       notconnect   119          auto   auto 10/100BaseTX
 Fa0/37                       notconnect   119          auto   auto 10/100BaseTX
 Fa0/38                       connected    119        a-full  a-100 10/100BaseTX
 Fa0/39                       notconnect   119          auto   auto 10/100BaseTX
 Fa0/40                       notconnect   119          auto   auto 10/100BaseTX
 Fa0/41                       notconnect   119          auto   auto 10/100BaseTX
 Fa0/42                       connected    119        a-full  a-100 10/100BaseTX
 Fa0/43                       notconnect   119          auto   auto 10/100BaseTX
 Fa0/44                       notconnect   119          auto   auto 10/100BaseTX
 Fa0/45                       connected    119        a-full  a-100 10/100BaseTX
 Fa0/46                       notconnect   119          auto   auto 10/100BaseTX
 Fa0/47    Port disabled - LA disabled     116          auto   auto 10/100BaseTX
 Fa0/48                       connected    116        a-full   a-10 10/100BaseTX
 Gi0/1                        connected    trunk      a-full  a-100 10/100/1000BaseTX SFP
 Gi0/2                        notconnect   1            auto   auto 10/100/1000BaseTX SFP
 Gi0/3                        notconnect   1            auto   auto Not Present
 Gi0/4                        notconnect   1            auto   auto Not Present
 sw-01>"""

print ("<process_show_interface>")

__interface_output = StringIO(__interface_output)
interface = DeviceInterface()

while True:
    # Go through line by line
    line = __interface_output.readline()

    if len(line) == 0:
        break

    items = line.strip()

    # prepare string
    # replace possible unnecessary whitespaces
    items = items.replace( ' SFP', '-SFP')
    items = items.replace( 'Not Present', 'NotPresent')
    #items = re.sub(' +',' ',items)
    items = items.split( )

# Show interface status have at least 6 col or 7
# Port, Name, Status, Vlan, Duplex, Speed, Type

    if len(items) >= 5:
        # if we have data
        items_number = len(items)

        if str(items[0][-1:]).isdigit():
            # if it is a port (a number)
            # if we have the right data
            # interface name
            interface.interfacename = items[0]
            # interface type
            interface.interfacetype = items[-1]
            #
            interface.accessvlan = items[-4]
            #
            interface.status = items[-5]

            __description = ""

            print("iterator size: ", len(items))
            iterator = 1
            while iterator <= len(items)-6:
                print("Item: ", items[iterator])
                __description += items[iterator]
                __description += ' '
                iterator = iterator+1

            __description.strip()
            print(items)
            print(interface.interfacename)
            print(interface.interfacetype)
            print(interface.accessvlan)
            print(interface.status)
            print("DESC: ",__description)


print ("</process_show_interface>")
