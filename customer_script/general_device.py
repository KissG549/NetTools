# general_device.py

from enum import Enum
import io, os, sys, time, getopt
import signal, struct, constant
from cStringIO import StringIO
import string
import logging


known_switches = ["WS-C3560CX-12PC-S", "WS-C3650-24TS-S", "WS-C3650-48TS", "WS-C3850-12S", "WS-C3850-12XS-S", "WS-C3850-24T", "WS-C3850-48T", "WS-C3650-24PS-S", "WS-C3650-48PS-S", "WS-C3650-48FS-S", "WS-C3850-24P-S", "WS-C3850-48P-S", "WS-C2924M-XL-A", "WS-C2940-8TT-S",  "WS-C2950-12", "WS-C2950-24", "WS-C2950C-24", "WS-C2950G-24-EI", "WS-C2950SX-24", "WS-C2950SX-48-SI", "WS-C2950T-24", "WS-C2950T-48-SI", "WS-C2960-24LC-S", "WS-C2960-24LT-L", "WS-C2960-24PC-L", "WS-C2960-24PC-S", "WS-C2960-24-S", "WS-C2960-24TC-L", "WS-C2960-24TC-S", "WS-C2960-24TT-L", "WS-C2960-48PST-L", "WS-C2960-48PST-S", "WS-C2960-48TC-L", "WS-C2960-48TC-S", "WS-C2960-48TT-L", "WS-C2960-8TC-L", "WS-C2960-8TC-S", "WS-C2960CG-8TC-L", "WS-C2960G-24TC-L", "WS-C2960G-48TC-L", "WS-C2960G-8TC-L", "WS-C2960S-24PS-L", "WS-C2960S-24TS-L", "WS-C2960S-24TS-S", "WS-C2960S-48FPS-L", "WS-C2960S-48LPS-L", "WS-C2960S-48TS-L", "WS-C2960S-48TS-S", "WS-C2960S-F24PS-L", "WS-C2960S-F48FPS-L", "WS-C3508G-XL-EN", "WS-C3550-48-SMI", "WS-C3560-12PC-S", "WS-C3560-24PS-E", "WS-C3560-24PS-S", "WS-C3560-24TS-S", "WS-C3560-48PS-E", "WS-C3560-48PS-S", "WS-C3560-48TS-E", "WS-C3560-48TS-S", "WS-C3560-8PC-S", "WS-C3560CG-8PC-S", "WS-C3560G-24PS-S", "WS-C3560G-24TS-E", "WS-C3560G-24TS-S", "WS-C3560G-24TS-S", "WS-C3560G-48PS-E", "WS-C3560V2-24PS-S", "WS-C3560V2-48PS-S", "WS-C3560X-24P-S", "WS-C3560X-24T-S", "WS-C3560X-48PF-S", "WS-C3750-24PS-S", "WS-C3750-24TS-E", "WS-C3750-48PS-S", "WS-C3750-48TS-S", "WS-C3750E-24PD-S", "WS-C3750E-24TD-E", "WS-C3750E-24TD-S", "WS-C3750E-48PD-SF", "WS-C3750G-12S-E", "WS-C3750G-12S-S", "WS-C3750G-24PS-E", "WS-C3750G-24PS-S", "WS-C3750G-24T-E", "WS-C3750G-24T-S", "WS-C3750G-24TS-E", "WS-C3750G-24TS-E1U", "WS-C3750G-24TS-S", "WS-C3750G-24TS-S1U", "WS-C3750G-24WS-S25", "WS-C3750G-48PS-S", "WS-C3750V2-24PS-S", "WS-C3750V2-48PS-E", "WS-C3750V2-48PS-S", "WS-C3750X-12S-E", "WS-C3750X-12S-S", "WS-C3750X-24P-L", "WS-C3750X-24P-S", "WS-C3750X-24S-E", "WS-C3750X-24S-S", "WS-C3750X-24S-S", "WS-C3750X-24T-L", "WS-C3750X-24T-S", "WS-C3750X-48P-E", "WS-C3750X-48P-L", "WS-C3750X-48P-S", "WS-C3750X-48T-L", "WS-C3750X-48T-S", "WS-C4506", "WS-C4507R", "WS-C4507R-E", "WS-C4948-10GE", "WS-C6513"]

known_access_points = ["AIR-LAP1041N-E-K9", "AIR-LAP1042N-A-K9", "AIR-LAP1042N-E-K9", "AIR-AP1042N-E-K9", "AIR-AP1121G-E-K9", "AIR-AP1131AG-E-K9", "AIR-AP1131G-E-K9", "AIR-LAP1131AG-E-K9", "AIR-LAP1131G-E-K9", "AIR-LAP1141N-E-K9", "AIR-AP1141N-E-K9", "AIR-LAP1142N-E-K9", "AIR-AP1142N-E-K9", "AIR-AP1220-IOS-UPGRD", "AIR-AP1230B-E-K9", "AIR-AP1231G-E-K9", "AIR-LAP1231G-E-K9", "AIR-AP1242AG-E-K9", "AIR-AP1242G-E-K9", "AIR-LAP1242AG-E-K9", "AIR-LAP1242G-E-K9", "AIR-LAP1262N-E-K9", "AIR-AP1262N-E-K9", "AIR-AP1572EAC-E-K9", "AIR-AP1832I-E-K9", "AIR-AP1852I-E-K9", "AIR-AP2702E-UXK9", "AIR-AP350", "AIR-CAP1532E-E-K9", "AIR-CAP1552H-E-K9", "AIR-CAP1602E-E-K9", "AIR-CAP1602I-E-K9", "AIR-LAP1602E-E-K9", "AIR-LAP1602I-E-K9", "AIR-SAP1602E-E-K9", "AIR-SAP1602I-E-K9", "AIR-CAP1702I-E-K9", "AIR-SAP1702I-E-K9", "AIR-CAP2602E-E-K9", "AIR-CAP2602I-E-K9", "AIR-SAP2602E-E-K9", "AIR-SAP2602I-E-K9", "AIR-CAP2702E-E-K9", "AIR-CAP2702I-E-K9", "AIR-SAP2702E-E-K9", "AIR-SAP2702I-E-K9", "AIR-CAP3602E-E-K9", "AIR-CAP3702E-E-K9", "AIR-CAP702I-E-K9", "AIR-LAP1252AG-E-K9", "AIR-LAP1261N-E-K9"]

DEBUG_LOGFILE = "/home/littleg/Dokumentumok/DEVELOPMENT_DIR/customer_script/my_pexpect.log"
DEVICE_OUTPUT_LOGFILE = "/home/littleg/Dokumentumok/DEVELOPMENT_DIR/customer_script/my_device_output_pexpect.log"
OUTPUT_FILE = "/home/littleg/Dokumentumok/DEVELOPMENT_DIR/customer_script/output.txt"

TWOMETER = "2m"
TRUNKTWOMETER = "2x2 m"

DEVICE_ID_CHARS = 16
LOCAL_INT_CHARS = 18
HOLDTIME_CHARS = 11
CAPABILITY_CHARS = 10
PLATFORM_CHARS = 10
PORT_ID_CHARS = 8
REMOTE_PORT_CHARS = 68

ACCESS = "access"
TRUNK = "trunk"

STATE_UP = "UP"
STATE_SHUTDOWN = "SHUTDOWN"

NOT_AVAILABLE_DATA = "N/A"
MISSING_DATA = "-"
TRUNK_PORT ="Trunk port"
ACCESS_PORT = "Access port"
GENERAL_PORT = "Eth0"
NOT_CONNECTED = "Not connected"

CONNECTED = "connected"
NOTCONNECTED = "notconnect"
DISABLED = "disabled"
ERRDISABLED = "err-disabled"

RJ45 = "TX"
RJ45_NAME = "RJ45"
GLCT = "TX-SFP"
GLCT_MODULENAME = "GLC-T"
GLCSXMMD = "SX-SFP"
GLCSX_MODULENAME = "GLC-SX-MMD="
GLCLHSMD = "LH-SFP"
GLCLHSMD_MODULENAME = "GLC-LH-SMD="
NOTPRESENT = "NotPresent"
OTHER = "other"

UTP = "Cat5e/Cat6   UTP"
LCtoLCMM = "Fiber patchcord - LC to LC - Multi Mode - must verify!"
LCtoLCSM = "Fiber patchcord - LC to LC - Single Mode - must verify!"


VTP_MODE_CLIENT = "Client"
VTP_MODE_SERVER = "Server"
VTP_MODE_TRANSPARENT = "Transparent"
VTP_MODE_NEW = "Transparent"

CDP_DEVICE_ID_STR = "Device ID:"
CDP_IP_ADDRESS_STR = "IP address:"
CDP_PLATFORM_STR = "Platform:"
CDP_INTERFACE_ID_STR = "Interface:"
CDP_PORT_ID_STR = "Port ID"
CDP_OUTGOING_PORT = "outgoing port"
CDP_ENTRY_SEPARATOR = "-------------------------"

class DevFunct(Enum):
    NULL = None
    WAN = "WAN"
    LAN = "LAN"
    WIFI = "WIFI"

class DevAction(Enum):
    NULL = 0
    KEEP = 1
    ADD = 2
    REPLACE = 3
    DECOMMISSION = 4

class PortType(Enum):
    NULL = 0
    ACCESS = "access"
    TRUNK = "trunk"

class ConnectionCabType(Enum):
    NULL = None
    UTP = "Cat5e/Cat6   UTP"
    LCtoLCMM = "Fiber patchcord - LC to LC - Multi Mode - must verify!"
    LCtoLCSM = "Fiber patchcord - LC to LC - Single Mode - must verify!"

class ConnectionCabLength(Enum):
    NULL = None
    TWOMETER = "2m"
    TRUNKTWOMETER = "2x2 m"

class InterfaceType(Enum):
#    def __init__(self):
#        self = NULL
    NULL = None
    RJ45 = "TX"
    RJ45_NAME = "RJ45"
    GLCT = "TX-SFP"
    GLCT_MODULENAME = "GLC-T"
    GLCSXMMD = "SX-SFP"
    GLCSX_MODULENAME = "GLC-SX-MMD="
    GLCLHSMD = "LH-SFP"
    GLCLHSMD_MODULENAME = "GLC-LH-SMD="
    NOTPRESENT = "NotPresent"
    OTHER = "other"

class InterfaceStatus(Enum):
    NULL = ""
    CONNECTED = "connected"
    NOTCONNECTED = "notconnect"
    DISABLED = "disabled"
    ERRDISABLED = "err-disabled"

class DeviceInterface:
    interfacename = None    # Name of the interface e.g.: GigabitEthernet 1/0/1 or Gig1/0/1
    interfacedescription = None # Description from port configuration
    interfacetype = None  # PortType RJ45, GLC-T, GLC-SX, GLC-LH
    allowedvlans = None # list of allowed vlans
    accessvlan = None
    voicevlan = None
    nativevlan = None
    status = None  # connected/notconnected/disabled/err-disabled
    isvirtual = None # True when it's VLAN interface
    IPaddress = None # IP address or list of IP addresses, if it's a L3 interface
    netmask = None # Netmask's for IP addresses
    neighborname = None
    neighborport = None
    neighboripaddress = None

class VlanClass:
    def __init__(self):
        self.name = None
        self.number = None
        self.state = None
        self.enabled = None

    number = None
    name = None
    enabled = None

class VTPModes(Enum):
    NULL = None
    VTP_MODE_CLIENT = "Client"
    VTP_MODE_SERVER = "Server"
    VTP_MODE_TRANSPARENT = "Transparent"

class NeighborEntry():
    device_id = None # Hostname or IP from LLDP or CDP
    address = None # IP address
    mgmt_address = None # MGMT IP address
    local_port = None # Where the remote device is conncted on this ( local )
    remote_port = None # The remote port of the connecion
    platform = None # Platform e.g: cisco WS-C2960G-24TC-L


class GeneralDevice(object):
    """ Class for store data of general device """
    #
    # Variables
    #
    siteID = None
    hostname = None
    MGMTIPaddress = None
    ports = [] # DeviceInterface list
    deviceFunction = DevFunct.NULL
    Location = None
    model = [] # must be list
    serial = [] # must be list
    module = []
    module_serial = []
    deviceAction = DevAction.NULL
    vlan_list = [] # VlanClass
    neighbor_list = [] # NeighborEntry
# Methods
#


    def print_inventory(self, __output_file):
        inventory_iterator = 0
        while inventory_iterator < len(self.model):

            print self.model[inventory_iterator]
            __output_file.write(self.model[inventory_iterator])
            print self.serial[inventory_iterator]
            __output_file.write(self.serial[inventory_iterator])
            print self.module[inventory_iterator]
            __output_file.write(self.module[inventory_iterator])
            print self.module_serial[inventory_iterator]
            __output_file.write(self.module_serial[inventory_iterator])
            inventory_iterator += 1
        # endwhile
    #enddef

    def print_datasource_inventory(self, __output_file):
        # DEVICE_HOSTNAME
        # DEVICE_FUNCTION
        # DEVICE_LOCATION
        # DEVICE_CURRENT_MODEL
        # DEVICE_CURRENT_SERIAL
        inventory_iterator = 0
        while inventory_iterator < len(self.model):
            if (len(self.model)>inventory_iterator):
                print("Model out of range!")
                break
            elif (len(self.module)>inventory_iterator):
                print("Module out of range!")
                break
            elif (len(self.module_serial)>inventory_iterator):
                print("Module_serial out of range!")
                break

            print( "%s;%s;Comms room;%s;%s;" % (self.hostname, self.model[inventory_iterator], self.model[inventory_iterator], self.module_serial[inventory_iterator]))
            __output_file.write("%s;%s;Comms room;%s;%s;\r\n" % (self.hostname, self.model[inventory_iterator], self.module[inventory_iterator], self.module_serial[inventory_iterator]))
            inventory_iterator +=1
        # endwhile
    # enddef

    # search in inventory variables and return true if it is
    def is_switch(self):

        global known_switches

        print( self.model )
        print(known_switches)
        inventory_iterator = 0
        while inventory_iterator < len(self.model):
            switch_iterator = 0
            while switch_iterator < len(known_switches):
                print("%s<->%s" % (self.model[inventory_iterator],known_switches[switch_iterator] ))
                if  self.model[inventory_iterator] in known_switches[switch_iterator]:
                    print("It's a switch!!!!!")
                    return True
                #endif
                switch_iterator += 1
            # endwhile
            inventory_iterator += 1
        # endewhile
        return False
    #enddef

    def is_access_point(self):
        inventory_iterator = 0
        while inventory_iterator < len(self.model):
            ap_iterator = 0
            while ap_iterator < len(known_access_points):
                if  self.model[inventory_iterator] in known_access_points[ap_iterator]:
                    print("It's an ap!!!!!")
                    return True
                #endif
                ap_iterator += 1
            # endwhile
            inventory_iterator += 1
        # endewhile
        return False
    #enddef

    def process_inventory( self,  __inventory_output ):
        self.model = []
        self.serial = []
        self.module = []
        self.module_serial = []

        print("<process_inventory>")
        #print(__inventory_output)

        __inventory_output = StringIO(__inventory_output)
        itisamodule = False
        while True:
            __product_id = ""
            __product_serial = ""
            __product_desc = ""
            line = __inventory_output.readline()

            if len(line) == 0:
                break
            words = line.split(':')
            words_number = len(words)
            # If the line is empty or less than the required, just pass to the next line.
            # At inventory we must have at least 3 parts
            if words_number < 3:
                continue

            if words[0] == "NAME" :
                # working with the first line
                print("%s" %str( words_number) )
                model_desc = words[2]
            #    re.sub('[\"]', '', model)
                model_desc = model_desc.translate(string.maketrans('', ''), '\"')
                model_desc = model_desc.strip()
                print( '<model_desc>%s</model_desc>' % (model_desc) )

                # split the line starting with NAME
                name_values = words[1].split(',')
                if len(name_values) > 0:
                    # Only the first part needed
                    # ' "1", DESCR' or ' "GigabitEthernet0/2", DESCR'
                    value = name_values[0]
                    # remove whitespaces and \" char
                    value = value.translate(string.maketrans('', ''), '\"')
                    value = value.strip()
                    print( '<value>%s</value>' % (value) )
                    # If it's digit, it must be the device and not the module

                    if  str(value).isdigit() == True:
                        # save switch
                        itisamodule = False
                    else:
                        itisamodule = True

            elif words[0] == "PID" :
                # if it's the product identifier line
                pid_values = words[1].split(',')
                if len(pid_values) > 0:
                    __product_id =  pid_values[0]
                    __product_id = __product_id.translate(string.maketrans('', ''), '\"')
                    __product_id = __product_id.strip()
                    print( '<PID>%s</PID>' % (__product_id) )

                # read the serial number
                __product_serial = words[3].strip()
                print("<serial_number>%s</serial_number>" % (__product_serial))

                if itisamodule == False:
                    # Save device parameters here
                    # print("Save switch parameters here")
                    self.model.append( __product_id )
                    self.serial.append( __product_serial )
                else:
                    # print("Save module parameters here")
                    if __product_id == "Unspecified":
                        __product_id = model_desc.replace( ' SFP', '-SFP')
                    #endif

                    self.module.append( __product_id )
                    self.module_serial.append( __product_serial )
            #print(words)
            #line = __inventory_output.readline()

        print("</process_inventory>")
        return

    def print_datasource_connections(self, __output_file):

        iterator = 0
        while iterator < len(self.ports):
            connections_site_id=""
            connections_deva=""
            connections_porta=""
            connections_vlan_number=""
            connections_connection_type=""
            connections_port_admin_state=""
            connections_native_vlan=""
            connections_voice_vlan=""
            connections_action=""
            connections_typea=""
            connections_devb=""
            connections_portb=""
            connections_typeb=""
            connections_cab_type=""
            connections_cab_length=""
            # CONNECTIONS_DEVA
            # print("CONNECTIONS_DEVA: ", self.hostname)
            connections_deva = self.hostname
            # CONNECTIONS_PORTA
            # print("CONNECTIONS_PORTA: ", self.ports[iterator].interfacename)
            connections_porta=self.ports[iterator].interfacename
            # CONNECTIONS_VLAN_NUMBER
            if self.ports[iterator].allowedvlans != None:
                # print("CONNECTIONS_VLAN_NUMBER: ", self.ports[iterator].allowedvlans)
                connections_vlan_number=self.ports[iterator].allowedvlans
            else:
                # print("CONNECTIONS_VLAN_NUMBER: ", self.ports[iterator].accessvlan)
                connections_vlan_number=self.ports[iterator].accessvlan

            # CONNECTIONS_CONNECTION_TYPE
            if self.ports[iterator].accessvlan == TRUNK:
            # ACCESS or trunk
                # print("CONNECTIONS_CONNECTION_TYPE: ", TRUNK)
                connections_connection_type=TRUNK
            else:
                # print("CONNECTIONS_CONNECTION_TYPE:", ACCESS)
                connections_connection_type=ACCESS

            # CONNECTIONS_PORT_ADMIN_STATE
            if self.ports[iterator].status == DISABLED:
                # print("CONNECTIONS_PORT_ADMIN_STATE: SHUTDOWN")
                connections_port_admin_state=STATE_SHUTDOWN
            else:
                # print("CONNECTIONS_PORT_ADMIN_STATE: UP")
                connections_port_admin_state=STATE_UP

            # CONNECTIONS_NATIVE_VLAN
            if self.ports[iterator].nativevlan!= None:
                # print("CONNECTIONS_NATIVE_VLAN: ", self.ports[iterator].nativevlan)
                connections_native_vlan=self.ports[iterator].nativevlan
            else:
                # print("CONNECTIONS_NATIVE_VLAN: N/A")
                connections_native_vlan=NOT_AVAILABLE_DATA

            # CONNECTIONS_VOICE_VLAN
            if self.ports[iterator].voicevlan!=None:
                # print("CONNECTIONS_VOICE_VLAN: ", self.ports[iterator].voicevlan)
                connections_voice_vlan = self.ports[iterator].voicevlan
            else:
                # print("CONNECTIONS_VOICE_VLAN: N/A")
                connections_voice_vlan=NOT_AVAILABLE_DATA

            # CONNECTIONS_ACTION
            # print("CONNECTIONS_ACTION: KEEP")
            connections_action="KEEP"

            if str(RJ45) in str(self.ports[iterator].interfacetype):
                if str(GLCT) in self.ports[iterator].interfacetype:
                    # print("CONNECTIONS_TYPEA-glct: ", GLCT_MODULENAME )
                    connections_typea=GLCT_MODULENAME
                else:
                    # print("CONNECTIONS_TYPEA-rj45: ", RJ45_NAME )
                    connections_typea=RJ45_NAME
                #endif
            elif str(GLCSXMMD) in str(self.ports[iterator].interfacetype):
                #print("CONNECTIONS_TYPEA-glcsx: ", GLCSX_MODULENAME )
                connections_typea=GLCSX_MODULENAME
            #endelif
            elif str(GLCLHSMD) in str(self.ports[iterator].interfacetype):
            #endelif
                #print("CONNECTIONS_TYPEA-glclh: ", GLCLHSMD_MODULENAME )
                connections_typea=GLCLHSMD_MODULENAME
            elif (str(NOTPRESENT) in str(self.ports[iterator].interfacetype) or
                (self.ports[iterator].status == DISABLED )):
                #print("CONNECTIONS_TYPEA-notpresent: -" )
                connections_typea=MISSING_DATA
            else:
                #print("CONNECTIONS_TYPEA-other: ", self.ports[iterator].interfacetype )
                connections_typea=self.ports[iterator].interfacetype
            #endif

            if ((str(NOTPRESENT) in str(self.ports[iterator].interfacetype)) or
                (self.ports[iterator].status == NOTCONNECTED or
                self.ports[iterator].status == NOTPRESENT )):
                # print("CONNECTIONS_DEVB: -")
                # print("CONNECTIONS_PORTB: -")
                # print("CONNECTIONS_TYPEB: -")
                # print("CONNECTIONS_CAB_TYPE: -")
                # print("CONNECTIONS_CAB_LENGTH: -")
                connections_devb=MISSING_DATA
                connections_portb=MISSING_DATA
                connections_typeb=MISSING_DATA
                connections_cab_type=MISSING_DATA
                connections_cab_length=MISSING_DATA
            # endif
            else:
                # CONNECTIONS_DEVB
                if self.ports[iterator].neighborname != None:
                    # print("CONNECTIONS_DEVB: ", self.ports[iterator].neighborname)
                    connections_devb=self.ports[iterator].neighborname
                elif self.ports[iterator].accessvlan == TRUNK:
                    #print("CONNECTIONS_DEVB: Trunk port")
                    connections_devb=TRUNK_PORT
                else:
                    #print("CONNECTIONS_DEVB: Access port")
                    connections_devb=ACCESS_PORT
                # endif
                # CONNECTIONS_PORTB
                if self.ports[iterator].neighborname != None:
                    if self.ports[iterator].neighborport != None:
                        # print("CONNECTIONS_PORTB: ", self.ports[iterator].neighborport)
                        connections_portb=self.ports[iterator].neighborport
                    else:
                        # print("CONNECTIONS_PORTB: N/A")
                        connections_portb=NOT_AVAILABLE_DATA
                    # endif
                # endif
                elif self.ports[iterator].accessvlan == TRUNK:
                    # print("CONNECTIONS_PORTB: N/A")
                    connections_portb=NOT_AVAILABLE_DATA
                else:
                    # print("CONNECTIONS_DEVB: Eth0")
                    connections_portb=GENERAL_PORT

                # endif

                # CONNECTIONS_TYPEB
                # CONNECTIONS_CAB_TYPE
                if str(RJ45) in str(self.ports[iterator].interfacetype):
                    # print("CONNECTIONS_TYPEB: ", RJ45_NAME )
                    # print("CONNECTIONS_CAB_TYPE: ", UTP )
                    connections_typeb=RJ45_NAME
                    connections_cab_type=UTP
                elif str(GLCSXMMD) in str(self.ports[iterator].interfacetype):
                    # print("CONNECTIONS_TYPEB: ", GLCSX_MODULENAME )
                    # print("CONNECTIONS_CAB_TYPE: ", LCtoLCMM )
                    connections_typeb=GLCSX_MODULENAME
                    connections_cab_type=LCtoLCMM
                #endelif
                elif str(GLCLHSMD) in str(self.ports[iterator].interfacetype):
                #endelif
                    # print("CONNECTIONS_TYPEA: ", GLCLHSMD_MODULENAME )
                    # print("CONNECTIONS_CAB_TYPE: ", LCtoLCSM )
                    connections_typea=GLCLHSMD_MODULENAME
                    connections_cab_type=LCtoLCSM
                elif str(NOTPRESENT) in str(self.ports[iterator].interfacetype):
                    # print("CONNECTIONS_TYPEA: not connected" )
                    # print("CONNECTIONS_CAB_TYPE: -" )
                    connections_typea=NOT_CONNECTED
                    connections_cab_type=MISSING_DATA
                else:
                    # print("CONNECTIONS_TYPEA: ", self.ports[iterator].interfacetype )
                    # print("CONNECTIONS_CAB_TYPE: N/A")
                    connections_typea=self.ports[iterator].interfacetype
                    connections_cab_type=NOT_AVAILABLE_DATA
                #endif

                # CONNECTIONS_CAB_LENGTH
                #print("Trunk or not? ", (self.ports[iterator].accessvlan == TRUNK))
                if self.ports[iterator].accessvlan == TRUNK:
                    # print("CONNECTIONS_CAB_LENGTH: ", TRUNKTWOMETER )
                    connections_cab_length=TRUNKTWOMETER
                else:
                    # print("CONNECTIONS_CAB_LENGTH: ", TWOMETER )
                    connections_cab_length=TWOMETER
            #endif

            iterator +=1


                    # CONNECTIONS_SITE_ID
                    # CONNECTIONS_DEVA
                    # CONNECTIONS_PORTA
                    # CONNECTIONS_VLAN_NUMBER
                    # CONNECTIONS_CONNECTION_TYPE
                    # CONNECTIONS_PORT_ADMIN_STATE
                    # CONNECTIONS_NATIVE_VLAN
                    # CONNECTIONS_VOICE_VLAN
                    # CONNECTIONS_ACTION
                    # CONNECTIONS_TYPEA
                    # CONNECTIONS_DEVB
                    # CONNECTIONS_PORTB
                    # CONNECTIONS_TYPEB
                    # CONNECTIONS_CAB_TYPE
                    # CONNECTIONS_CAB_LENGTH
            print("%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;" %
                (connections_site_id,connections_deva,connections_porta,connections_vlan_number,connections_connection_type,connections_port_admin_state,connections_native_vlan,connections_voice_vlan,connections_action,connections_typea,connections_devb,connections_portb,connections_typeb,connections_cab_type,connections_cab_length))
            __output_file.write("%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;\r\n" %
                (connections_site_id,connections_deva,connections_porta,connections_vlan_number,connections_connection_type,connections_port_admin_state,connections_native_vlan,connections_voice_vlan,connections_action,connections_typea,connections_devb,connections_portb,connections_typeb,connections_cab_type,connections_cab_length))

        #endwhile
        return

##################################################################################
    def print_connections(self):
        iterator = 0
        while iterator < len(self.ports):
            # CONNECTIONS_SITE_ID # Missing yet
            # CONNECTIONS_DEVA
            print("CONNECTIONS_DEVA: ", self.hostname)
            # CONNECTIONS_PORTA
            print("CONNECTIONS_PORTA: ", self.ports[iterator].interfacename)
            # CONNECTIONS_VLAN_NUMBER
            if self.ports[iterator].allowedvlans != None:
                print("CONNECTIONS_VLAN_NUMBER: ", self.ports[iterator].allowedvlans)
            else:
                print("CONNECTIONS_VLAN_NUMBER: ", self.ports[iterator].accessvlan)

            # CONNECTIONS_CONNECTION_TYPE
            if self.ports[iterator].accessvlan == TRUNK:
            # ACCESS or trunk
                print("CONNECTIONS_CONNECTION_TYPE: ", TRUNK)
            else:
                print("CONNECTIONS_CONNECTION_TYPE:", PortType.ACCESS)

            # CONNECTIONS_PORT_ADMIN_STATE
            if self.ports[iterator].status == DISABLED:
                print("CONNECTIONS_PORT_ADMIN_STATE: SHUTDOWN")
            else:
                print("CONNECTIONS_PORT_ADMIN_STATE: UP")

            # CONNECTIONS_NATIVE_VLAN
            if self.ports[iterator].nativevlan!= None:
                print("CONNECTIONS_NATIVE_VLAN: ", self.ports[iterator].nativevlan)
            else:
                print("CONNECTIONS_NATIVE_VLAN: N/A")

            # CONNECTIONS_VOICE_VLAN
            if self.ports[iterator].voicevlan!=None:
                print("CONNECTIONS_VOICE_VLAN: ", self.ports[iterator].voicevlan)
            else:
                print("CONNECTIONS_VOICE_VLAN: N/A")

            # CONNECTIONS_ACTION
            print("CONNECTIONS_ACTION: KEEP")

            # CONNECTIONS_TYPEA
            # print("Notpresent? ", (str(NOTPRESENT) in str(self.ports[iterator].interfacetype)))
            # print("GLCT? ", (str(GLCT) in str(self.ports[iterator].interfacetype)))
            # print("GLCSXMMD?", (str(GLCSXMMD) in str(self.ports[iterator].interfacetype)))
            # print("GLCSXMMD?", (str(GLCLHSMD) in str(self.ports[iterator].interfacetype)))

            if str(RJ45) in str(self.ports[iterator].interfacetype):
                if str(GLCT) in self.ports[iterator].interfacetype:
                    print("CONNECTIONS_TYPEA-glct: ", GLCT_MODULENAME )
                else:
                    print("CONNECTIONS_TYPEA-rj45: ", RJ45_NAME )
                #endif
            elif str(GLCSXMMD) in str(self.ports[iterator].interfacetype):
                print("CONNECTIONS_TYPEA-glcsx: ", GLCSX_MODULENAME )
            #endelif
            elif str(GLCLHSMD) in str(self.ports[iterator].interfacetype):
            #endelif
                print("CONNECTIONS_TYPEA-glclh: ", GLCLHSMD_MODULENAME )
            elif (str(NOTPRESENT) in str(self.ports[iterator].interfacetype) or
                (self.ports[iterator].status == DISABLED )):
                print("CONNECTIONS_TYPEA-notpresent: -" )
            else:
                print("CONNECTIONS_TYPEA-other: ", self.ports[iterator].interfacetype )
            #endif

            if (str(NOTPRESENT) in str(self.ports[iterator].interfacetype) or
                (self.ports[iterator].status != InterfaceStatus.CONNECTED )):
                print("CONNECTIONS_DEVB: -")
                print("CONNECTIONS_PORTB: -")
                print("CONNECTIONS_TYPEB: -")
                print("CONNECTIONS_CAB_TYPE: -")
                print("CONNECTIONS_CAB_LENGTH: -")
            # endif
            else:
                # CONNECTIONS_DEVB
                if self.ports[iterator].neighborname != None:
                    print("CONNECTIONS_DEVB: ", self.ports[iterator].neighborname )
                elif self.ports[iterator].accessvlan == TRUNK:
                    print("CONNECTIONS_DEVB: Trunk port")
                else:
                    print("CONNECTIONS_DEVB: Access port")
                # endif
                # CONNECTIONS_PORTB
                if self.ports[iterator].neighborname != None:
                    if self.ports[iterator].neighborport != None:
                        print("CONNECTIONS_PORTB: ", self.ports[iterator].neighborport)
                    else:
                        print("CONNECTIONS_PORTB: N/A")
                    # endif
                # endif
                elif self.ports[iterator].accessvlan == TRUNK:
                    print("CONNECTIONS_PORTB: N/A")
                else:
                    print("CONNECTIONS_DEVB: Eth0")
                # endif

                # CONNECTIONS_TYPEB
                # CONNECTIONS_CAB_TYPE
                if str(RJ45) in str(self.ports[iterator].interfacetype):
                    print("CONNECTIONS_TYPEB: ", RJ45_NAME )
                    print("CONNECTIONS_CAB_TYPE: ", UTP )
                elif str(GLCSXMMD) in str(self.ports[iterator].interfacetype):
                    print("CONNECTIONS_TYPEB: ", GLCSX_MODULENAME )
                    print("CONNECTIONS_CAB_TYPE: ", LCtoLCMM )

                #endelif
                elif str(GLCLHSMD) in str(self.ports[iterator].interfacetype):
                #endelif
                    print("CONNECTIONS_TYPEA: ", GLCLHSMD_MODULENAME )
                    print("CONNECTIONS_CAB_TYPE: ", LCtoLCSM )
                elif str(NOTPRESENT) in str(self.ports[iterator].interfacetype):
                    print("CONNECTIONS_TYPEA: not connected" )
                    print("CONNECTIONS_CAB_TYPE: -" )
                else:
                    print("CONNECTIONS_TYPEA: ", self.ports[iterator].interfacetype )
                    print("CONNECTIONS_CAB_TYPE: N/A")

                #endif

                # CONNECTIONS_CAB_LENGTH
                print("Trunk or not? ", (self.ports[iterator].accessvlan == TRUNK))
                if self.ports[iterator].accessvlan == TRUNK:
                    print("CONNECTIONS_CAB_LENGTH: ", TRUNKTWOMETER )
                else:
                    print("CONNECTIONS_CAB_LENGTH: ", TWOMETER )
            #endif

            #if self.ports[iterator].status ==
            #print("interfacedescription: ",self.ports[iterator].interfacedescription)
            # print("isvirtual: ",self.ports[iterator].isvirtual)
            # print("IPaddress: ",self.ports[iterator].IPaddress)
            # print("netmask: ",self.ports[iterator].netmask)
            # print("neighborname: ",self.ports[iterator].neighborname)
            # print("neighborport: ", self.ports[iterator].neighborport)
            # print("neighboripaddress: ",self.ports[iterator].neighboripaddress)
            print()
            iterator +=1
        #endwhile
        return

    def print_interface_params(self):
        iterator = 0
        while iterator < len(self.ports):
            print("InterfaceName: ",self.ports[iterator].interfacename)
            print("interfacedescription: ",self.ports[iterator].interfacedescription)
            print("interfacetype: ",self.ports[iterator].interfacetype)
            print("allowedvlans: ",self.ports[iterator].allowedvlans)
            print("accessvlan: ",self.ports[iterator].accessvlan)
            print("voicevlan: ",self.ports[iterator].voicevlan)
            print("nativevlan: ",self.ports[iterator].nativevlan)
            print("status: ",self.ports[iterator].status)
            print("isvirtual: ",self.ports[iterator].isvirtual)
            print("IPaddress: ",self.ports[iterator].IPaddress)
            print("netmask: ",self.ports[iterator].netmask)
            print("neighborname: ",self.ports[iterator].neighborname)
            print("neighborport: ", self.ports[iterator].neighborport)
            print("neighboripaddress: ",self.ports[iterator].neighboripaddress)
            print()
            iterator +=1
        return

    def process_show_interface( self, __interface_output ):
        print ("<process_show_interface>")

        __interface_output = StringIO(__interface_output)
        interface = None

        while True:
            interface = DeviceInterface()
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

                    # concatenate the description
                    # print("iterator size: ", len(items))
                    iterator = 1
                    while iterator <= len(items)-6:
                        #print("Item: ", items[iterator])
                        __description += items[iterator]
                        __description += ' '
                        iterator = iterator+1
                        __description.strip()
                    interface.interfacedescription = __description
                    self.ports.append( interface )
        print ("</process_show_interface>")
        return

    def process_trunk_output(self, __trunk_output):

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

            if (len(items) < 2) :
                continue

            # print("size: ", len(items))

            if(len(items) > 5 ) and (items[4] == 'Native'):
                is_allowed_section = False
                is_native_vlan_section = True
                continue
            if(len(items) ==5 ) and (items[2] == 'allowed'):
                is_allowed_vlan_section = True
                is_native_vlan_section = False
                continue
            if(items[0] == 'Port'):
                is_allowed_vlan_section = False
                is_native_vlan_section = False
                #continue
            if is_native_vlan_section:
                port = items[0]
                if len(items)>4:
                    native_vlan = items[4]
                    # print("Native VLAN: %s - %s" % (port, native_vlan))
                    # Save native VLAN and port here
                    port_iterator = 0
                    while port_iterator != len(self.ports):
                        if self.ports[port_iterator].interfacename == port:
                            self.ports[port_iterator].nativevlan = native_vlan
                            break
                        port_iterator+=1

            if is_allowed_vlan_section:
                port = items[0]
                allowed_vlans = items[1]
                # print("Allowed VLAN: %s - %s" % (port, allowed_vlans))
                port_iterator = 0
                while port_iterator != len(self.ports):
                    if self.ports[port_iterator].interfacename == port:
                        self.ports[port_iterator].allowedvlans = allowed_vlans
                        break
                    port_iterator+=1
                # Save allowed VLANS here

            print(items)

        print ("</process_trunk_output>")
        return

    def print_cdp_det_output(self, __output_file):
        # print the neighbor parameters
        cdp_iterator = 0
        while cdp_iterator < len(self.neighbor_list):
            neigh_entry = self.neighbor_list[cdp_iterator]
            print("%s;%s;%s;%s;%s;%s;%s" %
            (self.hostname, neigh_entry.device_id, neigh_entry.platform, neigh_entry.address, neigh_entry.mgmt_address, neigh_entry.local_port, neigh_entry.remote_port))
            __output_file.write("%s;%s;%s;%s;%s;%s;%s\r\n" %
            (self.hostname, neigh_entry.device_id, neigh_entry.platform, neigh_entry.address, neigh_entry.mgmt_address, neigh_entry.local_port, neigh_entry.remote_port))
            cdp_iterator += 1
        # endwhile
    # end def print_cdp_det_output(self):

    def process_cdp_det_output( self, __cdp_det_output ):

        neighbor = NeighborEntry()
        neighbor.device_id = ""
        neighbor.ip_address = ""
        neighbor.mgmt_ip_address = ""
        neighbor.local_port = ""
        neighbor.remote_port = ""
        neighbor.platform = ""


        __cdp_det_output = StringIO(__cdp_det_output)

        while True:

            line = __cdp_det_output.readline()

            items = line.split()

            print("items: ", items)

            if (len(line) == 0):
                break

            if (CDP_ENTRY_SEPARATOR in line):
                # save parameters here
                self.neighbor_list.append(neighbor)
                neighbor.device_id = ""
                neighbor.ip_address = ""
                neighbor.mgmt_ip_address = ""
                neighbor.local_port = ""
                neighbor.remote_port = ""
                neighbor.platform = ""

            elif ((CDP_DEVICE_ID_STR in line) and
                (len(items) > 2)):
                neighbor.device_id = items[2].split(".")
                neighbor.device_id = neighbor.device_id[0]

            elif ((CDP_IP_ADDRESS_STR in line) and
                (len(items) > 2)):
                if neighbor.ip_address == "":
                    # if the ip address is emtpy yet
                    neighbor.ip_address = items[2].strip()
                else:
                    # it must be the mgmt address item
                    neighbor.mgmt_ip_address = items[2].strip()
                # endelse
            elif ((CDP_PLATFORM_STR in line) and
                (len(items) > 2)):
                    line = line.split(",")
                    line = line[0]
                    line = line.strip()
                    line = line.split(":")
                    if len(line)>1:
                        neighbor.platform = line[1].strip()
                    # endif
            elif ((CDP_INTERFACE_ID_STR in line) and
                (len(items) > 6)):

                neighbor.local_port = items[1].strip()
                neighbor.remote_port = items[6]
        # endwhile

        #save last items here
        if neighbor.device_id != "":
            self.neighbor_list.append(neighbor)
        #endif

    # end     def process_cdp_det_output( self, __cdp_det_output ):

    def process_lldp_output( self, __lldp_output):
        print("<process_lldp_output>")
        print("Please implement process_lldp_output( self, __lldp_output)!")
        print("</process_lldp_output>")
        return

    def process_cdp_output( self, __cdp_output ):
        print ("<process_cdp_output>")
        # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        # print(__cdp_output)
        # print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
        __cdp_output = StringIO(__cdp_output)
        localport = ""
        remoteport = ""
        neighbor = ""
        neighbor_section = False

        while True:
            # Go through line by line
            line = __cdp_output.readline()
            items = line.split()
            # print("# of items: ", len(items))
            # if the line is empty (last line) or CDP is not enabled, then quit
            if (len(line) == 0) or ("not enabled" in line):
                break

            if (len(items) < 1):
                continue

            if items[0] == "Device":
                neighbor_section = True
                continue

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


                port_iterator = 0
                while port_iterator != len(self.ports):
                    #print("####>%s<#-#>%s<#" % (self.ports[port_iterator].interfacename,localport ))
                    if self.ports[port_iterator].interfacename == localport:
                            self.ports[port_iterator].neighborname = neighbor
                            self.ports[port_iterator].neighborport = remoteport
                            break
                    port_iterator+=1
                # Save parameters here
                #print("size: ", len(items))
                #print("neighbor: ", neighbor)
                #print("localport: ", localport)
                #print("remoteport: ", remoteport)

            # print(items)

        # END while loop

        print ("</process_cdp_output>")
        return

    def print_vlans(self, __output_file):
        vlan_item = VlanClass()

        vlan_iterator = 0
        while vlan_iterator != len(self.vlan_list):
            vlan_item = self.vlan_list[vlan_iterator]
            print("%s;%s;%s;%s" % (self.hostname, vlan_item.name, vlan_item.number, vlan_item.state))
            __output_file.write("%s;%s;%s;%s\r\n" % (self.hostname, vlan_item.name, vlan_item.number, vlan_item.state))
            vlan_iterator += 1
        # endwhile

        # end     def print_vlans(self):

    def process_show_vlan_brief(self, __vlan_output):
        global DEBUG_LOGFILE
        print ("<process_show_vlan_output>")
        logging.basicConfig(filename = DEBUG_LOGFILE, level=logging.DEBUG)

        __vlan_output = StringIO(__vlan_output)
        # vlan_list = [] # VlanClass - number and name
        ports_per_vlan = [] # two dimension list

        vlan_section = False
        VLAN_ID_CHARS = 5
        VLAN_NAME_CHARS = 33
        VLAN_STATUS_CHARS = 10
        PORT_CHARS = 48

        vlan_item = VlanClass()
        port = ""

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
            print("VLAN Items: ", items )
            # print("itemsitemsitemsitemsitemsitemsitemsitems")

            ### Process the output
            # IF we are in the vlan section and have enough items to work with
            # If this line is about VLANID, VLAN-description, VLAN-status and assigned ports then
            if (str(items[0]).isdigit() and
                (vlan_section) and
                len(items)>2):

                if vlan_item.number != None:
                    # save vlan item to the list
                    self.vlan_list.append(vlan_item)
                    # save port's to the list
                    ports_per_vlan.append(port)
                # endif

                vlan_item = VlanClass()
                vlan_item.number = items[0].strip()
                vlan_item.name = items[1].strip()
                vlan_item.state = items[2].strip()
                if len(items) > 3:
                    port = items[3].strip()
                else:
                    port = ""
                # endelse
            elif len(items) == 1:
                # else it must contain only ports for the prev vlan
                port += ","
                port += items[0].strip()
            # endif
        # endwhile
        # Last line must be added also to the list
        # save vlan item to the list
        self.vlan_list.append(vlan_item)
        # save port's to the list
        ports_per_vlan.append(port)

        # print("vlanvlanvlanvlanvlanvlanvlanvlan")
        # print(vlan_item.name)
        # print(vlan_item.number)
        # print("vlanvlanvlanvlanvlanvlanvlanvlan")

        print("PortPerVlan")
        print(ports_per_vlan)
        print("PortPerVlan")

        # go through in vlan list with
        vlan_iterator = 0
        while( vlan_iterator < len(self.vlan_list)):
            #print("VLAN-number: ", self.vlan_list[iterator].number)
            #print("VLAN-name: ", self.vlan_list[iterator].name)
            #print("Port:", ports_per_vlan[iterator])

            #print("-------")

            if vlan_iterator > len(ports_per_vlan):
                # if don't have enough item in vlans and the associated ports, then break the loop
                break

            try:
                #go through the ports
                __ports_loc = ports_per_vlan[vlan_iterator].split(",")
                # print("Ports are:", __ports_loc)
                ports_loc_iterator = 0
                while ports_loc_iterator != len(__ports_loc):

                    port_iterator = 0
                    while port_iterator != len(self.ports):
                        #print("####>%s<#-#>%s<#" % (self.ports[port_iterator].interfacename,__ports_loc[ports_loc_iterator] ))
                        if self.ports[port_iterator].interfacename == __ports_loc[ports_loc_iterator]:


                            if self.ports[port_iterator].accessvlan == None:
                                self.ports[port_iterator].accessvlan = self.vlan_list[vlan_iterator].number
                                # if it is, then set the current vlan as access vlan
                            elif self.ports[port_iterator].accessvlan != self.vlan_list[vlan_iterator].number:
                                # if not then set up as voice vlan
                                self.ports[port_iterator].voicevlan = self.vlan_list[vlan_iterator].number

                            # check vlan is empty or None
                            # print("VLAN: ", self.vlan_list[vlan_iterator].number)
                            # print("ACCESS-VLAN: ", self.ports[port_iterator].accessvlan)
                            # print("VOICE-VLAN: ", self.ports[port_iterator].voicevlan)
                            break
                        port_iterator+=1

                    #end while
                    ports_loc_iterator+=1
                #endwhile
            except:
                globals()
                locals()
            vlan_iterator +=1

        print ("</process_show_vlan_output>")
        return

    def process_show_vtp_status(self, __vtp_output):
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
        self.VTP.VTPDomain = vtp_domain
        self.VTP.VTPMode = vtp_mode
        print ("</process_show_vtp_output>")
        return

    def print_datasource_vtp_info(self, __output_file):
        # VTP_SITE_ID	VTP_CHANGE_ORDER	VTP_HOSTNAME	VTP_MODE_EXISTING	VTP_MODE_NEW	VTP_DOMAIN_NAME
        print(";;%s;%s;%s;%s" % (self.hostname, self.VTP.VTPMode, VTP_MODE_NEW, self.VTP.VTPDomain))
        __output_file.write(";;%s;%s;%s;%s\r\n" % (self.hostname, self.VTP.VTPMode, VTP_MODE_NEW, self.VTP.VTPDomain))
        return

# end class GeneralDevice(object):


class VTPClass:
    VTPMode = None
    VTPDomain = None

class SwitchClass(GeneralDevice):
    VTP = VTPClass()
    isitstack = None


#
# Methods
#
