# Parse output from cisco devices
# classes and constants from my_classes

from __future__ import print_function

from __future__ import absolute_import

from enum import Enum

import io, os, sys, time, getopt
import signal, struct, constant
import pexpect
import re

from cStringIO import StringIO
import string

import logging

from my_classes import *

#
#   Parse functions here
#

class CiscoParser:
    # Name convention: parse_{command_name}

    my_device = None
    # SwitchClass

    def parse_show_inventory(self,output):
        import my_print
        import my_classes
        self.my_device.model = []
        self.my_device.serial = []
        self.my_device.module = []
        self.my_device.module_serial = []


        __product_id = str()
        __product_serial = str()
        __product_desc = str()

        _print = my_print.Print()
        output = StringIO(output)

        itisamodule=False
        while True:
            __product_id = ""
            __product_serial = ""
            __product_desc = ""
            line = output.readline()

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
                _print.my_print(("%s" %str( words_number)), printlevel_loc = my_classes.PrintLevel.INFORMATION, printdestination_loc = my_classes.PrintDestination.STDOUT)
                model_desc = str()
                model_desc = words[2]
            #    re.sub('[\"]', '', model)
                model_desc = model_desc.translate(string.maketrans('', ''), '\"')
                model_desc = model_desc.strip()
                _print.my_print( '<model_desc>%s</model_desc>' % (model_desc) , printlevel_loc = my_classes.PrintLevel.DEBUG)

                # split the line starting with NAME
                name_values = str()
                name_values = words[1].split(',')
                if len(name_values) > 0:
                    # Only the first part needed
                    # ' "1", DESCR' or ' "GigabitEthernet0/2", DESCR'
                    value = name_values[0]
                    # remove whitespaces and \" char
                    value = value.translate(string.maketrans('', ''), '\"')
                    value = value.strip()
                    _print.my_print( '<value>%s</value>' % (value) , printlevel_loc = my_classes.PrintLevel.DEBUG)
                    # If it's digit, it must be the device and not the module

                    if  str(value).isdigit() == True:
                        # save switch
                        itisamodule = False
                    else:
                        itisamodule = True

            elif words[0] == "PID" :
                # if it's the product identifier line
                pid_values = str()
                pid_values = words[1].split(',')
                if len(pid_values) > 0:
                    __product_id =  pid_values[0]
                    __product_id = __product_id.translate(string.maketrans('', ''), '\"')
                    __product_id = __product_id.strip()
                    _print.my_print( '<PID>%s</PID>' % (__product_id) , printlevel_loc = my_classes.PrintLevel.DEBUG)

                # read the serial number
                __product_serial = words[3].strip()
                _print.my_print("<serial_number>%s</serial_number>" % (__product_serial), printlevel_loc = my_classes.PrintLevel.DEBUG)

                if itisamodule == False:
                    # Save device parameters here
                    # print("Save switch parameters here")
                    self.my_device.model.append( __product_id )
                    self.my_device.serial.append( __product_serial )
                else:
                    # or save here
                    if __product_id == "Unspecified":
                        __product_id = model_desc.replace( ' SFP', '-SFP')
                    #endif

                    #_print.my_print("Product ID and serial added: %s ; %s" % (__product_id,__product_serial) )
                    self.my_device.module.append( __product_id )
                    self.my_device.module_serial.append( __product_serial )

            print("Model-1: ",self.my_device.model)
            print("Model-1 serial: ",self.my_device.serial)
            print("Mydevice: ", self.my_device.hostname)
            #print(words)
            #line = __inventory_output.readline()

        # Normalize list, remove duplicated items here

        #if len(self.my_device.model) > 0:
        #    inventory_iterator = 0
        #    while inventory_iterator < (len(self.my_device.model)-1):
        #        if self.my_device.serial[inventory_iterator] == self.my_device.serial[len(self.my_device.serial)-1]:
        #            self.my_device.model.pop()
        #            self.my_device.serial.pop()
        #            self.my_device.module.pop()
        #            self.my_device.module_serial.pop()
        #            break
        #        inventory_iterator += 1
            # endwhile
        return
        # enddef

    def parse_show_ip_interface_brief( self, output ):
        import my_print
        import my_classes

        _print = my_print.Print()
        output = StringIO(output)
        interface = my_classes.DeviceInterface()

        while True:
            # Go through line by line
            line = output.readline()

            if len(line) == 0:
                break

            items = line.split()
            items_number = len(items)
            # prepare string
            # replace possible unnecessary whitespaces

            #print("# of ITEMS: ",items_number )
            #print("items: ", items )


            if len(items) >= 6:
                # if we have data
                # if we have more than 1 item, it's not the IP helper section
                if ((my_classes.INT_INTERFACE_STR in line) or
                    (my_classes.INT_UNASSIGNED_STR in line)):
                    # not necessary to work with this line
                    continue

                if items[INT_OK_ID] == INT_OK_YES_STR:
                    # if the interface is ok

                    interface.interfacename = my_classes.get_short_portname(items[INT_INTERFACE_ID])
                    interface.IPaddress = items[INT_IPADDR_ID].strip()

                    port_exist = False
                    port_iterator = 0
                    while port_iterator < len(self.my_device.ports):

                        if self.my_device.ports[port_iterator].interfacename == interface.interfacename:
                            # Already have the interface
                            #print( "Already have this interface: %s" % interface.interfacename)
                            #self.my_device.ports[port_iterator].interfacedescription = interface.interfacedescription
                            self.my_device.ports[port_iterator].IPaddress = interface.IPaddress
                            port_exist = True
                            break
                            # endif
                        port_iterator += 1
                    # endwhile

                    if ((interface.interfacename != None) and
                        not port_exist):
                        # don't have the interface just add it
                        #print("Don't have this interface yet: %s" % interface.interfacename)
                        #print("line_:", line)
                        self.my_device.ports.append( interface )
                    # endif

                    interface = my_classes.DeviceInterface()
            # endwhile
        return output
        # enddef

    def parse_show_ip_interface_details( self, output ):
        import my_print
        import my_classes

        _print = my_print.Print()
        output = StringIO(output)
        interface = my_classes.DeviceInterface()
        interface.helperaddresses = []
        is_helper_section = False

        while True:
            # Go through line by line
            line = output.readline()

            if len(line) == 0:
                break

            items = line.split()
            items_number = len(items)
            # prepare string
            # replace possible unnecessary whitespaces

            #print("# of ITEMS: ",items_number )
            #print("items: ", items )


            if len(items) >= 3:
                # if we have data
                # if we have more than 1 item, it's not the IP helper section
                is_helper_section = False

                if my_classes.LINE_PROTO_STR in line:
                    # the first line contains line protocol
                    # save parameters here because it's the first line
                    port_exist = False
                    port_iterator = 0
                    while port_iterator < len(self.my_device.ports):

                        if self.my_device.ports[port_iterator].interfacename == interface.interfacename:
                            # Already have the interface
                            #print( "Already have this interface: %s" % interface.interfacename)
                            #self.my_device.ports[port_iterator].interfacedescription = interface.interfacedescription
                            self.my_device.ports[port_iterator].IPaddress = interface.IPaddress
                            self.my_device.ports[port_iterator].helperaddresses = interface.helperaddresses
                            port_exist = True
                            break
                            # endif
                        port_iterator += 1
                    # endwhile

                    if ((interface.interfacename != None) and
                        not port_exist):
                        # don't have the interface just add it
                        #print("Don't have this interface yet: %s" % interface.interfacename)
                        #print("line_:", line)
                        self.my_device.ports.append( interface )
                    # endif

                    interface = my_classes.DeviceInterface()
                    interface.helperaddresses = []

                    interface.interfacename = items[0].strip()
                    interface.interfacename = my_classes.get_short_portname(interface.interfacename)

                elif my_classes.INT_DESCRIPTION_STR in line:
                    if my_classes.INT_DISABLED_STR not in line:
                        # if not disabled and may have IP address
                        interface.interfacedescription = line[ len(items[0])+1:].strip()
                elif my_classes.INT_INTERNET_STR in line:
                    interface.IPaddress = items[3].strip()
                elif my_classes.INT_HELPER_STR in line:
                    is_helper_section = True
                #end if
            elif len(items) == 1:
                if is_helper_section:
                    interface.helperaddresses.append( items[0] )
                # endif
            # endif
        return output
        # enddef

    def parse_show_interface( self, output ):
        import my_print
        import my_classes

        _print = my_print.Print()
        output = StringIO(output)
        interface = None

        while True:
            interface = my_classes.DeviceInterface()
            # Go through line by line
            line = output.readline()

            if len(line) == 0:
                break

            items = line.strip()

            # prepare string
            # replace possible unnecessary whitespaces
            items = items.replace( ' SFP', '-SFP')
            items = items.replace( 'Not Present', 'NotPresent')
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
                    iterator = 1
                    while iterator <= len(items)-6:
                        #print("Item: ", items[iterator])
                        __description += items[iterator]
                        __description += ' '
                        iterator = iterator+1
                        __description.strip()
                    interface.interfacedescription = __description
                    self.my_device.ports.append( interface )
                    #_print.my_print(("#of ports:%s" % (len(self.my_device.ports))))
        return
        # enddef

    def parse_show_standby_brief( self, output ):
        import my_print
        import my_classes

        _print = my_print.Print()
        output = StringIO(output)


        while True:
            # Go through line by line
            line = output.readline()


            if len(line) == 0:
                break

            items = line.split()
            items_number = len(items)
            # prepare string
            # replace possible unnecessary whitespaces

            #print("# of ITEMS: ",items_number )
            #print("items: ", items )


            if len(items) >= my_classes.HSRP_MAX_ITEMS_IN_LINE:
                # if we have data

                if (not(
                    (str(items[my_classes.HSRP_GROUP_ID]).isdigit()) and
                    (str(items[my_classes.HSRP_PRIO_ID]).isdigit()))):
                    # if the HSRP GROUP ID and the PRIORITY is not a number just skip this line
                        continue
                else:
                    port_exist = False
                    port_iterator = 0
                    while port_iterator < len(self.my_device.ports):

                        if self.my_device.ports[port_iterator].interfacename == items[my_classes.HSRP_INTERFACE_ITEM_ID]:
                            #print( "Already have this interface: %s" % interface.interfacename)
                            #self.my_device.ports[port_iterator].interfacedescription = interface.interfacedescription
                            self.my_device.ports[port_iterator].hsrpaddresses = items[my_classes.HSRP_VIRTUAL_ID]
                            self.my_device.ports[port_iterator].hsrpactivenodeaddresses = items[my_classes.HSRP_STANDBY_ID]
                            break
                            # endif
                        port_iterator += 1
                    # endwhile
                #end if
            # endif
        return
    # enddef

    def parse_show_int_trunk( self, output ):
        import my_print
        import my_classes

        _print = my_print.Print()
        output = StringIO(output)
        interface = DeviceInterface()
        port = ""
        allowed_vlans = ""
        native_vlan = ""
        is_native_vlan_section = False
        is_allowed_vlan_section = False

        while True:
            # Go through line by line
            line = output.readline()
            items = line.split()

            if len(line) == 0:
                break

            if (len(items) < 2):
                continue

            # print("size: ", len(items))

            if(len(items) > 5 ) and (items[4] == my_classes.VLAN_NATIVE_STR):
                is_allowed_section = False
                is_native_vlan_section = True
                continue
            if(len(items) ==5 ) and (items[2] == my_classes.VLAN_ALLOWED_STR):
                is_allowed_vlan_section = True
                is_native_vlan_section = False
                continue
            if(items[0] == my_classes.PORT_STR):
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
                    while port_iterator != len(self.my_device.ports):
                        if self.my_device.ports[port_iterator].interfacename == port:
                            self.my_device.ports[port_iterator].nativevlan = native_vlan
                            break
                        port_iterator+=1

            if is_allowed_vlan_section:
                port = items[0]
                allowed_vlans = items[1]
                # print("Allowed VLAN: %s - %s" % (port, allowed_vlans))
                port_iterator = 0
                while port_iterator != len(self.my_device.ports):
                    if self.my_device.ports[port_iterator].interfacename == port:
                        self.my_device.ports[port_iterator].allowedvlans = allowed_vlans
                        break
                    port_iterator+=1
                # Save allowed VLANS here

            _print.my_print(items, printdestination_loc = my_classes.PrintDestination.STDOUT)
        return
        # enddef

    def parse_show_cdp( self, output ):
        import my_print
        import my_classes

        _print = my_print.Print()
        output = StringIO(output)
        localport = ""
        remoteport = ""
        neighbor = ""
        neighbor_section = False

        while True:
            # Go through line by line
            line = output.readline()
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
                if(len(line[0:my_classes.DEVICE_ID_NUMCHARS].strip()) != 0 ):
                    # Dev id is not empty
                    neighbor = line[0:my_classes.DEVICE_ID_NUMCHARS].strip()
                # END if
                localport = line[my_classes.DEVICE_ID_NUMCHARS:my_classes.DEVICE_ID_NUMCHARS+my_classes.LOCAL_INT_NUMCHARS].strip()
                localport = localport.replace(" ", "")
                localport = localport[:2] + localport[3:]
                remoteport = line[(my_classes.REMOTE_PORT_NUMCHARS):].strip()
                remoteport = remoteport.replace(" ", "")
                remoteport = remoteport[:2] + remoteport[3:]


                port_iterator = 0
                while port_iterator != len(self.my_device.ports):
                    #print("####>%s<#-#>%s<#" % (self.ports[port_iterator].interfacename,localport ))
                    if self.my_device.ports[port_iterator].interfacename == localport:
                            self.my_device.ports[port_iterator].neighborname = neighbor
                            self.my_device.ports[port_iterator].neighborport = remoteport
                            break
                    port_iterator+=1
                # Save parameters here

            # print(items)

        # END while loop
        return

        # enddef

    def parse_show_cdp_det( self, output ):
        import my_print
        import my_classes
        _print = my_print.Print()

        neighbor = NeighborEntry()
        neighbor.device_id = ""
        neighbor.ip_address = ""
        neighbor.mgmt_ip_address = ""
        neighbor.local_port = ""
        neighbor.remote_port = ""
        neighbor.platform = ""


        output = StringIO(output)

        while True:

            line = output.readline()
            items = line.split()
            _print.my_print("items: %s" % (items), printlevel_loc = my_classes.PrintLevel.DEBUG, printdestination_loc = my_classes.PrintDestination.STDOUT)

            if (len(line) == 0):
                break

            if (my_classes.CDP_ENTRY_SEPARATOR_STR in line):
                # skip empty lines
                # save parameters here
                if ((neighbor.device_id != "") and
                    (neighbor.ip_address != "") and
                    (neighbor.mgmt_ip_address != "") and
                    (neighbor.local_port != "") and
                    (neighbor.remote_port != "") and
                    (neighbor.platform != "")):
                        self.my_device.neighbor_list.append(neighbor)
                    # endif

                neighbor = NeighborEntry()
                neighbor.device_id = ""
                neighbor.ip_address = ""
                neighbor.mgmt_ip_address = ""
                neighbor.local_port = ""
                neighbor.remote_port = ""
                neighbor.platform = ""

            elif ((my_classes.CDP_DEVICE_ID_STR in line) and
                (len(items) > 2)):
                neighbor.device_id = items[2].split(".")
                neighbor.device_id = neighbor.device_id[0]

            elif ((my_classes.CDP_IP_ADDRESS_STR in line) and
                (len(items) > 2)):
                if len(neighbor.ip_address) == 0:
                    # if the ip address is empty yet
                    neighbor.ip_address = items[2].strip()
                    #print("NEIGHBOR IP: ", neighbor.ip_address )
                else:
                    # it must be the mgmt address item
                    neighbor.mgmt_ip_address = items[2].strip()

                # endelse
            elif ((my_classes.CDP_PLATFORM_STR in line) and
                (len(items) > 2)):
                    line = line.split(",")
                    line = line[0]
                    line = line.strip()
                    line = line.split(":")
                    if len(line)>1:
                        neighbor.platform = line[1].strip()
                    # endif
            elif ((my_classes.CDP_INTERFACE_ID_STR in line) and
                (len(items) > 6)):

                neighbor.local_port = items[1].strip()
                neighbor.remote_port = items[6]
        # endwhile

        #save last items here
        if neighbor.device_id != "":
            self.my_device.neighbor_list.append(neighbor)
        return

        # enddef

    def parse_lldp_output( self, output ):
        import my_print
        import my_classes
        _print = my_print.Print()

        _print.my_print("parse_lldp_output( self, output ) not implemented!!", printlevel_loc = PrintLevel.INFORMATION, printdestination_loc = PrintDestination.ALL)

        return

        # enddef

    def parse_show_vlan_brief( self, output ):
        import my_print
        import my_classes

        _print = my_print.Print()
        output = StringIO(output)
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
            line = output.readline()
            line = line.replace(", ",",")
            items = line.split()

            # if the line is empty (last line) or LLDP is not enabled, then quit
            if (len(line) == 0) or ("Ambiguous" in line):
                break

            if (len(items) < 1) or ("---------" in line):
                continue

            if items[0] == "VLAN":
                vlan_section = True
                continue

            #_print.my_print( ("VLAN Items: %s" % (items)) , printlevel_loc = my_classes.PrintLevel.DEBUG, printdestination_loc = my_classes.PrintDestination.STDOUT)
            # print("itemsitemsitemsitemsitemsitemsitemsitems")

            ### Process the output
            # IF we are in the vlan section and have enough items to work with
            # If this line is about VLANID, VLAN-description, VLAN-status and assigned ports then
            if (str(items[0]).isdigit() and
                (vlan_section) and
                len(items)>2):

                if vlan_item.number != None:
                    # save vlan item to the list
                    self.my_device.vlan_list.append(vlan_item)
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
        self.my_device.vlan_list.append(vlan_item)
        # save port's to the list
        ports_per_vlan.append(port)

        _print.my_print("PortPerVlan", printlevel_loc = my_classes.PrintLevel.DEBUG, printdestination_loc = my_classes.PrintDestination.STDOUT)
        _print.my_print(ports_per_vlan, printlevel_loc = my_classes.PrintLevel.DEBUG, printdestination_loc = my_classes.PrintDestination.STDOUT)
        _print.my_print("PortPerVlan", printlevel_loc = my_classes.PrintLevel.DEBUG, printdestination_loc = my_classes.PrintDestination.STDOUT)

        # go through in vlan list with
        vlan_iterator = 0
        while( vlan_iterator < len(self.my_device.vlan_list)):

            if vlan_iterator > len(ports_per_vlan):
                # if don't have enough item in vlans and the associated ports, then break the loop
                break

            try:
                #go through the ports
                __ports_loc = ports_per_vlan[vlan_iterator].split(",")
                ports_loc_iterator = 0
                while ports_loc_iterator != len(__ports_loc):

                    port_iterator = 0
                    while port_iterator != len(self.my_device.ports):
                        #print("####>%s<#-#>%s<#" % (self.ports[port_iterator].interfacename,__ports_loc[ports_loc_iterator] ))
                        if self.my_device.ports[port_iterator].interfacename == __ports_loc[ports_loc_iterator]:


                            if self.my_device.ports[port_iterator].accessvlan == None:
                                self.my_device.ports[port_iterator].accessvlan = self.my_device.vlan_list[vlan_iterator].number
                                # if it is, then set the current vlan as access vlan
                            elif self.my_device.ports[port_iterator].accessvlan != self.my_device.vlan_list[vlan_iterator].number:
                                # if not then set up as voice vlan
                                self.my_device.ports[port_iterator].voicevlan = self.my_device.vlan_list[vlan_iterator].number

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

        return

        # enddef

    def parse_show_vtp_status( self, output ):
        import my_print
        import my_classes

        _print = my_print.Print()
        output = StringIO(output)

        vtp_domain = ""
        vtp_mode = ""

        while True:
            # Go through line by line
            line = output.readline()
            #print( line )
            items = line.split()

            # if the line is empty (last line) or LLDP is not enabled, then quit
            if (len(line) == 0):
                break

            if (len(items) < 1) or ("--------------" in line):
                continue

            if items[0] == my_classes.VTP_STR:

                if (( len(items) == 5) and
                    (items[1] == my_classes.DOMAIN_STR)):

                    vtp_domain = items[4].strip()
                elif (( len(items) == 5) and
                    (items[1] == my_classes.OPERATING_STR)):

                    vtp_mode = items[4].strip()
            #endif

        _print.my_print(vtp_domain, printlevel_loc = my_classes.PrintLevel.DEBUG, printdestination_loc = my_classes.PrintDestination.STDOUT)
        _print.my_print(vtp_mode, printlevel_loc = my_classes.PrintLevel.DEBUG, printdestination_loc = my_classes.PrintDestination.STDOUT)

        self.my_device.VTP.VTPDomain = vtp_domain
        self.my_device.VTP.VTPMode = vtp_mode
        return

    # enddef

    def parse_ap_show_version_isleightweight( self, output ):
        import my_print
        import my_classes

        _print = my_print.Print()
        output = StringIO(output)

        while True:
            # Go through line by line
            line = output.readline()
            #print( line )
            items = line.split()

            if (len(line) == 0):
                break

            if (len(items) < 1):
                continue

            if my_classes.VERSION_SOFTWARE_STR in line:
                if my_classes.AP_LEIGHTWEIGHT_SIGN_STR in line:
                    return True
                # endif
            #endif

        return False
    # enddef
