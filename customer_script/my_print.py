# PrintLevel# datastructures and methods

from enum import Enum, unique
import io, os, sys, time, getopt
import signal, struct, constant
from cStringIO import StringIO
import string
import logging

#from my_classes import *from my_classes import *
from my_classes import *

logfileisopened = False

logfile = ""

# Constants

class Print:
    import my_classes

    printlevel_loc= my_classes.PrintLevel.DEBUG
    from my_classes import PrintLevel

    def open_log(self, logfilename = LOGFILE ):
        global logfileisopened
        global logfile

        if not logfileisopened:
            logfile = open(logfilename, "wb")
            logfileisopened = True

        return logfile

    def close_log():
        global logfile

        logfile.close()
        return

    def my_print(self, __message, printlevel_loc = PrintLevel.DEBUG, printdestination_loc = PrintDestination.ALL  ):
        import my_classes

        global logfile

        ##
        #   __message = the printable message
        # printlevel_loc = the level of the current message
        # printdestination_loc = the destination of the message

        self.open_log()

        # if the print level is lower than the global level then just quit

        if ((len(__message )<1) or
            (printlevel_loc == PrintLevel.NULL) or
            (printdestination_loc == my_classes.PrintDestination.NULL)):
                return
        # endif

        if((self.printlevel_loc== PrintLevel.INFORMATION) and
            (printlevel_loc == PrintLevel.INFORMATION)):
                if printdestination_loc == my_classes.PrintDestination.STDOUT:
                    print(__message)
                elif printdestination_loc == my_classes.PrintDestination.LOGFILE:
                    logfile.write(__message)
                elif printdestination_loc == my_classes.PrintDestination.ALL:
                    print(__message)
                    logfile.write(__message )
                    logfile.write( "\n" )

        elif((self.printlevel_loc== PrintLevel.DEBUG) and
            ((printlevel_loc == PrintLevel.DEBUG) or (printlevel_loc == PrintLevel.INFORMATION))):
                if printdestination_loc == my_classes.PrintDestination.STDOUT:
                    print(__message)
                elif printdestination_loc == my_classes.PrintDestination.LOGFILE:
                    logfile.write(__message)
                elif printdestination_loc == my_classes.PrintDestination.ALL:
                    print(__message)
                    logfile.write(__message )
                    logfile.write( "\n" )

        # endif
    # enddef

    def print_inventory(self, __device):
        import my_classes
        # device is a GeneralDevice
        inventory_iterator = 0
        while inventory_iterator < len(__device.model):

            if len(__device.model) >= inventory_iterator:
                self.my_print( __device.model[inventory_iterator] , printlevel_loc= PrintLevel.INFORMATION)
            if len(__device.serial) >= inventory_iterator:
                self.my_print( __device.serial[inventory_iterator] , printlevel_loc= PrintLevel.INFORMATION)
            if len(__device.module) >= inventory_iterator:
                self.my_print( __device.module[inventory_iterator] , printlevel_loc= PrintLevel.INFORMATION)
            if len(__device.module_serial) >= inventory_iterator:
                self.my_print( __device.module_serial[inventory_iterator] , printlevel_loc= PrintLevel.INFORMATION)

            inventory_iterator += 1
            # endwhile

        #enddef

    def print_datasource_inventory(self, __device, output_file):
        import my_classes
        # DEVICE_HOSTNAME
        # DEVICE_FUNCTION
        # DEVICE_LOCATION
        # DEVICE_CURRENT_MODEL
        # DEVICE_CURRENT_SERIAL
        print("<printinventory>")

        inventory_iterator = 0
        while inventory_iterator < len(__device.model):
            if (len(__device.model)<=inventory_iterator):
                self.my_print("Model out of range! Model size: %s" % len(__device.model))
                break
            elif (len(__device.module)<=inventory_iterator):
                self.my_print("Module out of range! Module size %s" % len(__device.module))
                break
            elif (len(__device.module_serial)<=inventory_iterator):
                self.my_print("Module_serial out of range! Module serial size: %s" %len(__device.module_serial))
                break

            if isinstance(__device, my_classes.SwitchClass):

                print( "%s;%s;Comms room;%s;%s;" % (__device.hostname, __device.model[inventory_iterator], __device.model[inventory_iterator], __device.module_serial[inventory_iterator]))

                self.my_print(( "%s;%s;Comms room;%s;%s;" % (__device.hostname, __device.model[inventory_iterator], __device.model[inventory_iterator], __device.module_serial[inventory_iterator])), printlevel_loc = PrintLevel.INFORMATION)
                output_file.write(( "%s;%s;Comms room;%s;%s;\n" % (__device.hostname, __device.model[inventory_iterator], __device.model[inventory_iterator], __device.module_serial[inventory_iterator])))
            elif isinstance(__device, my_classes.AccessPointClass):
                print( "%s;%s;Comms room;%s;%s;" % (__device.hostname, __device.model[inventory_iterator], __device.model[inventory_iterator], __device.module_serial[inventory_iterator]))
                __leightweight_str = AP_NOT_LEIGHTWEIGHT_STR

                if __device.is_leightweight:
                    __leightweight_str = AP_LEIGHTWEIGHT_STR

                self.my_print(( "%s;%s;Comms room;%s;%s;%s" % (__device.hostname, __device.model[inventory_iterator], __device.model[inventory_iterator], __device.module_serial[inventory_iterator], my_classes.AP_LEIGHTWEIGHT_STR)), printlevel_loc = PrintLevel.INFORMATION)
                output_file.write(( "%s;%s;Comms room;%s;%s;%s\n" % (__device.hostname, __device.model[inventory_iterator], __device.model[inventory_iterator], __device.module_serial[inventory_iterator], my_classes.AP_LEIGHTWEIGHT_STR)))

            inventory_iterator+=1
        # endwhile
        print("</printinventory>")

    # enddef

    def print_deviceinfofordrawing(self, __device, output_file):
        import my_classes
        # DEVICE_HOSTNAME
        # DEVICE_FUNCTION
        # DEVICE_LOCATION
        # DEVICE_CURRENT_MODEL
        # DEVICE_CURRENT_SERIAL

        __inventorys = str()
        __ip_addresses = str()

        inventory_iterator = 0
        while inventory_iterator < len(__device.model):
            if (len(__device.model)<=inventory_iterator):
                self.my_print("Model out of range! Model size: %s" % len(__device.model))
                break
            elif (len(__device.module)<=inventory_iterator):
                self.my_print("Module out of range! Module size %s" % len(__device.module))
                break
            elif (len(__device.module_serial)<=inventory_iterator):
                self.my_print("Module_serial out of range! Module serial size: %s" %len(__device.module_serial))
                break

            # collect and concatenate inventory's
            __inventorys += __device.model[inventory_iterator]
            __inventorys += "\r\n"


            inventory_iterator+=1
        # endwhile

        port_iterator = 0
        while port_iterator < len(__device.ports):
            if __device.ports[port_iterator].IPaddress != None:
                ip_iterator = 0

                __ip_addresses += ("%s: %s\r\n") % (__device.ports[port_iterator].interfacename,__device.ports[port_iterator].IPaddress)
                if ((len(__device.ports[port_iterator].hsrpaddresses) > 0)):
                    __ip_addresses += ("%s-HSRP: %s\r\n") % (__device.ports[port_iterator].interfacename,__device.ports[port_iterator].hsrpaddresses)
                # endif

            port_iterator += 1

        print( "%s;%s;%s;" % (__device.hostname, __inventorys, __ip_addresses))

        self.my_print( "%s;%s;%s" % (__device.hostname, __inventorys, __ip_addresses))
        output_file.write( "%s;%s;%s\n" % (__device.hostname, __inventorys, __ip_addresses))

    # enddef

    def print_datasource_connections(self, __device, output_file):
        import my_classes

        iterator = 0
        while iterator < len(__device.ports):
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
            connections_deva = __device.hostname
            # CONNECTIONS_PORTA
            connections_porta=__device.ports[iterator].interfacename
            # CONNECTIONS_VLAN_NUMBER
            if __device.ports[iterator].allowedvlans != None:
                connections_vlan_number=__device.ports[iterator].allowedvlans
            else:
                connections_vlan_number=__device.ports[iterator].accessvlan

            # CONNECTIONS_CONNECTION_TYPE
            if __device.ports[iterator].accessvlan == my_classes.TRUNK_STR:
            # ACCESS or trunk
                connections_connection_type=my_classes.TRUNK_STR
            else:
                connections_connection_type=my_classes.ACCESS_STR

            if __device.ports[iterator].status == my_classes.DISABLED_STR:
                connections_port_admin_state=my_classes.STATE_SHUTDOWN_STR
            else:
                connections_port_admin_state=my_classes.STATE_UP_STR

            # CONNECTIONS_NATIVE_VLAN
            if __device.ports[iterator].nativevlan!= None:
                connections_native_vlan=__device.ports[iterator].nativevlan
            else:
                connections_native_vlan=my_classes.NOT_AVAILABLE_DATA_STR

            # CONNECTIONS_VOICE_VLAN
            if __device.ports[iterator].voicevlan!=None:
                connections_voice_vlan = __device.ports[iterator].voicevlan
            else:
                connections_voice_vlan=my_classes.NOT_AVAILABLE_DATA_STR

            # CONNECTIONS_ACTION
            connections_action="KEEP"

            if str(my_classes.RJ45_STR) in str(__device.ports[iterator].interfacetype):
                if str(my_classes.GLCT_STR) in __device.ports[iterator].interfacetype:
                    connections_typea=my_classes.GLCT_MODULENAME_STR
                else:
                    connections_typea=my_classes.RJ45_NAME_STR
                #endif
            elif str(my_classes.GLCSXMMD_STR) in str(__device.ports[iterator].interfacetype):
                connections_typea=my_classes.GLCSX_MODULENAME_STR
            #endelif
            elif str(my_classes.GLCLHSMD_STR) in str(__device.ports[iterator].interfacetype):
            #endelif
                connections_typea=my_classes.GLCLHSMD_MODULENAME_STR
            elif (str(my_classes.NOTPRESENT_STR) in str(__device.ports[iterator].interfacetype) or
                (__device.ports[iterator].status == my_classes.DISABLED_STR )):
                connections_typea=my_classes.MISSING_DATA_STR
            else:
                connections_typea=__device.ports[iterator].interfacetype
            #endif

            if ((str(my_classes.NOTPRESENT_STR) in str(__device.ports[iterator].interfacetype)) or
                (__device.ports[iterator].status == my_classes.NOTCONNECTED_STR or
                __device.ports[iterator].status == my_classes.NOTPRESENT_STR )):
                connections_devb=my_classes.NOTCONNECTED_STR
                connections_portb=my_classes.MISSING_DATA_STR
                connections_typeb=my_classes.MISSING_DATA_STR
                connections_cab_type=my_classes.MISSING_DATA_STR
                connections_cab_length=my_classes.MISSING_DATA_STR
            # endif
            else:
                # CONNECTIONS_DEVB
                if __device.ports[iterator].neighborname != None:
                    connections_devb=__device.ports[iterator].neighborname
                elif __device.ports[iterator].accessvlan == my_classes.TRUNK_STR:
                    connections_devb=my_classes.TRUNK_PORT_STR
                else:
                    connections_devb=my_classes.ACCESS_PORT_STR
                # endif
                # CONNECTIONS_PORTB
                if __device.ports[iterator].neighborname != None:
                    if __device.ports[iterator].neighborport != None:
                        connections_portb=__device.ports[iterator].neighborport
                    else:
                        connections_portb=my_classes.NOT_AVAILABLE_DATA_STR
                    # endif
                # endif
                elif __device.ports[iterator].accessvlan == my_classes.TRUNK_STR:
                    connections_portb=my_classes.NOT_AVAILABLE_DATA_STR
                else:
                    connections_portb=my_classes.GENERAL_PORT_STR

                # endif

                if str(my_classes.RJ45_STR) in str(__device.ports[iterator].interfacetype):
                    connections_typeb=my_classes.RJ45_NAME_STR
                    connections_cab_type=my_classes.UTP_STR
                elif str(my_classes.GLCSXMMD_STR) in str(__device.ports[iterator].interfacetype):
                    connections_typeb=my_classes.GLCSX_MODULENAME_STR
                    connections_cab_type=my_classes.LCtoLCMM_STR
                #endelif
                elif str(my_classes.GLCLHSMD_STR) in str(__device.ports[iterator].interfacetype):
                #endelif
                    connections_typea=my_classes.GLCLHSMD_MODULENAME_STR
                    connections_cab_type=my_classes.LCtoLCSM_STR
                elif str(my_classes.NOTPRESENT_STR) in str(__device.ports[iterator].interfacetype):
                    connections_typea=my_classes.NOT_CONNECTED_STR
                    connections_cab_type=my_classes.MISSING_DATA_STR
                else:
                    connections_typea=__device.ports[iterator].interfacetype
                    connections_cab_type=my_classes.NOT_AVAILABLE_DATA_STR
                #endif

                # CONNECTIONS_CAB_LENGTH
                #print("Trunk or not? ", (self.ports[iterator].accessvlan == TRUNK))
                if __device.ports[iterator].accessvlan == my_classes.TRUNK_STR:
                    # print("CONNECTIONS_CAB_LENGTH: ", TRUNKTWOMETER )
                    connections_cab_length=my_classes.TRUNKTWOMETER_STR
                else:
                    # print("CONNECTIONS_CAB_LENGTH: ", TWOMETER )
                    connections_cab_length=my_classes.TWOMETER_STR
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
            self.my_print(("%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;" %
                (connections_site_id,connections_deva,connections_porta,connections_vlan_number,connections_connection_type,connections_port_admin_state,connections_native_vlan,connections_voice_vlan,connections_action,connections_typea,connections_devb,connections_portb,connections_typeb,connections_cab_type,connections_cab_length)),printlevel_loc = PrintLevel.INFORMATION)

            # Save output to specific file

            output_file.write("%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;\n" %
                (connections_site_id,connections_deva,connections_porta,connections_vlan_number,connections_connection_type,connections_port_admin_state,connections_native_vlan,connections_voice_vlan,connections_action,connections_typea,connections_devb,connections_portb,connections_typeb,connections_cab_type,connections_cab_length))

        #endwhile
        return

    def print_datasource_vtp_status(self, __device, output_file):
        import my_classes

        if isinstance(__device, my_classes.SwitchClass):
            # if it's a switch
            # VTP_SITE_ID	VTP_CHANGE_ORDER	VTP_HOSTNAME	VTP_MODE_EXISTING	VTP_MODE_NEW	VTP_DOMAIN_NAME
            self.my_print((";;%s;%s;%s;%s" % (__device.hostname, __device.VTP.VTPMode, my_classes.VTP_MODE_NEW_STR, __device.VTP.VTPDomain)),printlevel_loc= PrintLevel.INFORMATION)
            # __output_file.write(";;%s;%s;%s;%s\r\n" % (self.hostname, self.VTP.VTPMode, VTP_MODE_NEW, self.VTP.VTPDomain))
            output_file.write(";;%s;%s;%s;%s\n" % (__device.hostname, __device.VTP.VTPMode, my_classes.VTP_MODE_NEW_STR, __device.VTP.VTPDomain))
        
        return

    def print_datasource_vlans(self, __device, output_file):
        import my_classes
        vlan_item = VlanClass()

        vlan_iterator = 0
        while vlan_iterator != len(__device.vlan_list):
            vlan_item = __device.vlan_list[vlan_iterator]
            self.my_print("%s;%s;%s;%s" % (__device.hostname, vlan_item.name, vlan_item.number, vlan_item.state), PrintLevel.INFORMATION)
            output_file.write("%s;%s;%s;%s\n" % (__device.hostname, vlan_item.name, vlan_item.number, vlan_item.state))
            vlan_iterator += 1
        return


    def print_show_interface(self, __device ):
        import my_classes
        iterator = 0
        while iterator < len(__device.ports):
            self.my_print("InterfaceName: ",__device.ports[iterator].interfacename)
            self.my_print("interfacedescription: ",__device.ports[iterator].interfacedescription)
            self.my_print("interfacetype: ",__device.ports[iterator].interfacetype)
            self.my_print("allowedvlans: ",__device.ports[iterator].allowedvlans)
            self.my_print("accessvlan: ",__device.ports[iterator].accessvlan)
            self.my_print("voicevlan: ",__device.ports[iterator].voicevlan)
            self.my_print("nativevlan: ",__device.ports[iterator].nativevlan)
            self.my_print("status: ",__device.ports[iterator].status)
            self.my_print("isvirtual: ",__device.ports[iterator].isvirtual)
            self.my_print("IPaddress: ",__device.ports[iterator].IPaddress)
            self.my_print("netmask: ",__device.ports[iterator].netmask)
            self.my_print("neighborname: ",__device.ports[iterator].neighborname)
            self.my_print("neighborport: ", __device.ports[iterator].neighborport)
            self.my_print("neighboripaddress: ",__device.ports[iterator].neighboripaddress)
            self.my_print("------------")
            iterator+=1
        return

    def print_ip_interfaces( self, __device, outputfile):
        import my_classes
        port_iterator = 0
        while port_iterator < len(__device.ports):
            if __device.ports[port_iterator].IPaddress != None:
                __helper_addr = str("")
                #self.my_print("%s;%s;%s" % (__device.ports[iterator].interfacename, __device.ports[iterator].status,__device.ports[iterator].IPaddress ))
                #outputfile.write("%s;%s;%s;" % (__device.ports[iterator].interfacename, __device.ports[iterator].status,__device.ports[iterator].IPaddress ))
                if __device.ports[port_iterator].helperaddresses != None:
                    number_of_helpers = len(__device.ports[port_iterator].helperaddresses)
                    if number_of_helpers > 0:
                        helper_iterator = 0
                        while helper_iterator < number_of_helpers:
                            __helper_addr = str(("%s%s") %(__helper_addr,__device.ports[port_iterator].helperaddresses[helper_iterator] ))
                            if helper_iterator < number_of_helpers-1:
                            # if not the last item, then add a separator
                                __helper_addr += ","
                            # endif
                            helper_iterator += 1
                        # endwhile
                    #endif
                #endif
                self.my_print("%s;%s;%s;%s;%s" % (__device.hostname,__device.ports[port_iterator].interfacename, __device.ports[port_iterator].status,__device.ports[port_iterator].IPaddress, __helper_addr))
                outputfile.write("%s;%s;%s;%s;%s\n" % (__device.hostname,__device.ports[port_iterator].interfacename, __device.ports[port_iterator].status,__device.ports[port_iterator].IPaddress, __helper_addr))

            port_iterator+=1
        return

    def print_show_int_trunk(self, __device):
        import my_classes

        self.my_print("%s;%s;%s;%s" % (__device.hostname, vlan_item.name, vlan_item.number, vlan_item.state), printlevel_loc = PrintLevel.INFORMATION, printdestination_loc = PrintDestination.ALL)
        return

    def print_show_cdp(self, __device):
        import my_classes
        self.my_print("print_show_cdp(self, __device) not implemented!!", printlevel_loc = PrintLevel.INFORMATION, printdestination_loc = PrintDestination.ALL)

        return

    def print_show_cdp_det(self, __device, output_file):
        import my_classes

        # print the neighbor parameters
        cdp_iterator = 0
        while cdp_iterator < len(__device.neighbor_list):
            neigh_entry = __device.neighbor_list[cdp_iterator]
            self.my_print(("%s;%s;%s;%s;%s;%s;%s" %
            (__device.hostname, neigh_entry.device_id, neigh_entry.platform, neigh_entry.ip_address, neigh_entry.mgmt_ip_address, neigh_entry.local_port, neigh_entry.remote_port)), printlevel_loc = PrintLevel.INFORMATION )
            output_file.write(("%s;%s;%s;%s;%s;%s;%s\n" %
                (__device.hostname, neigh_entry.device_id, neigh_entry.platform, neigh_entry.ip_address, neigh_entry.mgmt_ip_address, neigh_entry.local_port, neigh_entry.remote_port)))

            cdp_iterator += 1
        # endwhile
    # end def print_cdp_det_output(self):
        return

    def print_lldp_output(self, __device):
        import my_classes
        self.my_print("print_lldp_output(self, __device) not implemented!!", printlevel_loc = PrintLevel.INFORMATION, printdestination_loc = PrintDestination.ALL)

        return

    def print_show_vlan_brief(self, __device):
        import my_classes
        self.my_print("print_show_vlan_brief(self, __device) not implemented!!", printlevel_loc = PrintLevel.INFORMATION, printdestination_loc = PrintDestination.ALL)

        return

    def print_show_vtp_status(self, __device):
        import my_classes
        self.my_print("print_show_vtp_status(self, __device) not implemented!!",  printlevel_loc = PrintLevel.INFORMATION, printdestination_loc = PrintDestination.ALL)

        return

    def print_device_information(self, devices_list):
        import my_classes

        device_iterator = 0
        curr_round = 0
        MAX_ROUND = 7 # number of parameters

    #    inventory_output_file = my_classes.create_and_open_outputfile(prefix = ("%s%s") % (my_classes.OUTPUT_FILE_DIRECTORY, my_classes.INVENTORY_OUTPUT_FILENAME_PREFIX))
    #    connection_output_file = my_classes.create_and_open_outputfile(prefix = ("%s%s") % (my_classes.OUTPUT_FILE_DIRECTORY,my_classes.CONNECTION_TABLE_OUTPUT_FILENAME_PREFIX))
    #    vtp_status_output_file = my_classes.create_and_open_outputfile(prefix = ("%s%s") % (my_classes.OUTPUT_FILE_DIRECTORY,my_classes.VTP_STATUS_OUTPUT_FILENAME_PREFIX))
    #    vlans_output_file = my_classes.create_and_open_outputfile(prefix = ("%s%s") % (my_classes.OUTPUT_FILE_DIRECTORY,my_classes.VLANS_OUTPUT_FILENAME_PREFIX))
    #    cdp_output_file = my_classes.create_and_open_outputfile(prefix = ("%s%s") % (my_classes.OUTPUT_FILE_DIRECTORY,my_classes.CDP_OUTPUT_FILENAME_PREFIX))


        #
        # Create and open files
        #

        while device_iterator < len(devices_list):

            if curr_round == 0:
                #print("<datasource_inventory>")
                self.my_print("<datasource_inventory>",  printlevel_loc = PrintLevel.INFORMATION, printdestination_loc = PrintDestination.ALL)
                self.print_datasource_inventory(devices_list[device_iterator], my_classes.inventory_file)
                self.my_print("</datasource_inventory>",  printlevel_loc = PrintLevel.INFORMATION, printdestination_loc = PrintDestination.ALL)

            elif curr_round == 1:
                self.my_print("<datasource_connections>",  printlevel_loc = PrintLevel.INFORMATION, printdestination_loc = PrintDestination.ALL)
                self.print_datasource_connections(devices_list[device_iterator], my_classes.connection_table_file)
                self.my_print("</datasource_connections>",  printlevel_loc = PrintLevel.INFORMATION, printdestination_loc = PrintDestination.ALL)
            elif curr_round == 2:
                self.my_print("<datasource_vtp>",  printlevel_loc = PrintLevel.INFORMATION, printdestination_loc = PrintDestination.ALL)
                self.print_datasource_vtp_status(devices_list[device_iterator], my_classes.vtp_status_file)
                self.my_print("</datasource_vtp>",  printlevel_loc = PrintLevel.INFORMATION, printdestination_loc = PrintDestination.ALL)
            elif curr_round == 3:
                self.my_print("<datasource_vlans>",  printlevel_loc = PrintLevel.INFORMATION, printdestination_loc = PrintDestination.ALL)
                self.print_datasource_vlans(devices_list[device_iterator], my_classes.vlans_file)
                self.my_print("</atasource_vlans>",  printlevel_loc = PrintLevel.INFORMATION, printdestination_loc = PrintDestination.ALL)
            elif curr_round == 4:
                self.my_print("<datasource_cdp>",  printlevel_loc = PrintLevel.INFORMATION, printdestination_loc = PrintDestination.ALL)
                self.print_show_cdp_det(devices_list[device_iterator], my_classes.cdp_file)
                self.my_print("</datasource_cdp>",  printlevel_loc = PrintLevel.INFORMATION, printdestination_loc = PrintDestination.ALL)
            elif curr_round == 5:
                self.my_print("<ip_addr>",  printlevel_loc = PrintLevel.INFORMATION, printdestination_loc = PrintDestination.ALL)
                self.print_ip_interfaces(devices_list[device_iterator], my_classes.ip_addr_file)
                self.my_print("</ip_addr>",  printlevel_loc = PrintLevel.INFORMATION, printdestination_loc = PrintDestination.ALL)
            elif curr_round == 6:
                self.my_print("<device_info_for_drawing>",  printlevel_loc = PrintLevel.INFORMATION, printdestination_loc = PrintDestination.ALL)
                self.print_deviceinfofordrawing(devices_list[device_iterator], my_classes.devinffordrawing_file)
                self.my_print("</device_info_for_drawing>",  printlevel_loc = PrintLevel.INFORMATION, printdestination_loc = PrintDestination.ALL)

            device_iterator += 1

            if device_iterator >= len(devices_list):
                if( curr_round < MAX_ROUND ):
                    curr_round += 1
                    device_iterator = 0
                # endif
            # endif
    # endwhile
