# New main file

#!/usr/bin/env python

from __future__ import print_function

from __future__ import absolute_import

import io, os, sys, time, getopt
import signal, struct, constant
import pexpect
import re # for filter

import my_classes
#from my_classes import *
from my_print import *
from cisco_parser import *

failed_connections_filename = OUTPUT_FILE_DIRECTORY
failed_connections_filename += "failed_ips.txt"
failed_connections_file = None

# Read devices informations (device name, device type, serial number, uplink, port settings, etc. )
# Read switch informations
def read_information_access_point():

    import my_print
    import my_classes
    import cisco_parser

    __print = Print()

    #global my_classes.child
    #
    # Set expect parameters
    #
    my_classes.child.delaybeforesend = 1
    my_classes.child.delayafterread = 2
    my_classes.child.timeout = my_classes.COMMAND_TIMEOUT
    #
    # Initiate variables
    #
    parser = cisco_parser.CiscoParser()
    parser.my_device = my_classes.AccessPointClass()
    parser.my_device.siteID = None
    parser.my_device.hostname = None
    parser.my_device.MGMTIPaddress = None
    parser.my_device.ports = [] # DeviceInterface list
    parser.my_device.deviceFunction = DevFunct.NULL
    parser.my_device.Location = None
    parser.my_device.model = [] # must be list
    parser.my_device.serial = [] # must be list
    parser.my_device.module = []
    parser.my_device.module_serial = []
    parser.my_device.deviceAction = DevAction.NULL
    parser.my_device.vlan_list = [] # VlanClass
    parser.my_device.neighbor_list = [] # NeighborEntry
    parser.my_device.helperaddresses = [] # list of IP addresses

    current_prompt = ""
    is_access_point = False
    #
    # Give some output to the user
    #
    __print.my_print("->Start to read information from access point->", printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT)
    # Save the current prompt
    my_classes.child.sendline(my_classes.NEWLINE_STR)
    current_prompt = ("%s%s" % (my_classes.child.before,my_classes.child.after))
    current_prompt = str.strip(current_prompt)
    # Set the terminal length to 0
    __response = cmd( my_classes.CISCO_CMD_TERM_LENG_INF )
    __print.my_print(__response, printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT)
    #
    # send newline
    #
    my_classes.child.sendline(my_classes.NEWLINE_STR)
    # waiting for command prompt
    try:
        my_classes.child.expect(my_classes.CISCO_COMMAND_PROMPT, timeout=my_classes.COMMAND_TIMEOUT)
        __response = ("%s"% (my_classes.child.before))
    except:
        __print.my_print("Command timed out, nothing to do. Continue.", printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT) # nothing to-do

    # print("<enter>%s<->%s</enter>" % (my_classes.child.before,my_classes.child.after))
    #
    # Save the hostname here and print
    #
    parser.my_device.hostname = __response.splitlines()
    parser.my_device.hostname = parser.my_device.hostname[len(parser.my_device.hostname)-1]
    parser.my_device.hostname = parser.my_device.hostname.strip()
    current_prompt = parser.my_device.hostname
    __print.my_print("HOSTNAME:::::::::>%s<" % (parser.my_device.hostname), printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT) # nothing to-do

    #
    # read inventory
    #
    # clear the buffer
    my_classes.child.buffer = ""

    inventory_output = cmd(my_classes.CISCO_CMD_SHOW_INV)
#    print( inventory_output )
    __print.my_print(inventory_output, printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT) # nothing to-do

    # process with inventory output
    parser.parse_show_inventory(inventory_output)

    # print the known access point to the user
    print( known_access_points )
    # check it's really an AP or not
    inventory_iterator = 0
    print("model size: ", len(parser.my_device.model))

    # prepare variables, my_device.model don't filled in the parse section, we need to move data
    parser.my_device.model =  parser.my_device.module
    parser.my_device.serial =  parser.my_device.module_serial

    while inventory_iterator < len(parser.my_device.model):
        ap_iterator = 0


        while ap_iterator < len(known_access_points):
            if  parser.my_device.model[inventory_iterator] in known_access_points[ap_iterator]:
                __print.my_print("It's an AP!!!!!", printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT)

                is_access_point = True
                parser.my_device.deviceFunction = DevFunct.WIFI
                break
            #endif
            ap_iterator += 1
            # endwhile
        inventory_iterator += 1

    if( not is_access_point ):
        __print.my_print(("It's NOT an AP: %s!!!!!" % parser.my_device.model), printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT)
        # if not an AP, we don't need to continue, then quit
        return False

    version_output = cmd(my_classes.CISCO_CMD_SHOW_VERSION)

    __print.my_print(version_output, printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT) # nothing to-do

    parser.my_device.is_leightweight = parser.parse_ap_show_version_isleightweight(version_output)

    my_classes.devices_list.append(parser.my_device)

    #
    # READ interface details output
    #
    #

    ip_interface_brief_output = cmd(my_classes.CISCO_CMD_SHOW_IP_INTERFACE_BRIEF)

    parser.parse_show_ip_interface_brief(ip_interface_brief_output)


    __print.my_print("<-End read information from access point->", printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT)

    return True

# enddef

def read_information_switch():
    import my_print
    import my_classes
    import cisco_parser

    __print = Print()

    #global my_classes.child
    my_classes.child.delaybeforesend = 1
    my_classes.child.delayafterread = 2
    my_classes.child.timeout = my_classes.COMMAND_TIMEOUT

    parser = cisco_parser.CiscoParser()
    parser.my_device = my_classes.SwitchClass()
    parser.my_device.VTP = VTPClass()
    parser.my_device.siteID = None
    parser.my_device.hostname = None
    parser.my_device.MGMTIPaddress = None
    parser.my_device.ports = [] # DeviceInterface list
    parser.my_device.deviceFunction = DevFunct.NULL
    parser.my_device.Location = None
    parser.my_device.model = [] # must be list
    parser.my_device.serial = [] # must be list
    parser.my_device.module = []
    parser.my_device.module_serial = []
    parser.my_device.deviceAction = DevAction.NULL
    parser.my_device.vlan_list = [] # VlanClass
    parser.my_device.neighbor_list = [] # NeighborEntry
    parser.my_device.helperaddresses = [] # list of IP addresses

    current_prompt = ""
    is_switch = False
    __print.my_print("->Start read information from switch->", printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT)
    my_classes.child.sendline(my_classes.NEWLINE_STR)
    current_prompt = ("%s%s" % (my_classes.child.before,my_classes.child.after))
    current_prompt = str.strip(current_prompt)
    # Set the terminal length to 0
    __response = cmd( my_classes.CISCO_CMD_TERM_LENG_INF )
    __print.my_print(__response, printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT)
    #
    # send enter
    #
    my_classes.child.sendline(my_classes.NEWLINE_STR)
    # waiting for command prompt
    try:
        my_classes.child.expect(my_classes.CISCO_COMMAND_PROMPT, timeout=my_classes.COMMAND_TIMEOUT)
        __response = ("%s"% (my_classes.child.before))
    except:
        __print.my_print("Command timed out, nothing to do. Continue.", printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT) # nothing to-do

    # print("<enter>%s<->%s</enter>" % (my_classes.child.before,my_classes.child.after))
    parser.my_device.hostname = __response.splitlines()
    parser.my_device.hostname = parser.my_device.hostname[len(parser.my_device.hostname)-1]
    parser.my_device.hostname = parser.my_device.hostname.strip()
    current_prompt = parser.my_device.hostname
    __print.my_print("HOSTNAME:::::::::>%s<" % (parser.my_device.hostname), printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT) # nothing to-do

    #
    # read inventory
    #
    my_classes.child.buffer = ""

    inventory_output = cmd(my_classes.CISCO_CMD_SHOW_INV)
    print( inventory_output )
    __print.my_print(inventory_output, printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT) # nothing to-do

    # process with inventory output
    parser.parse_show_inventory(inventory_output)

    print( known_switches )
    inventory_iterator = 0
    while inventory_iterator < len(parser.my_device.model):
        switch_iterator = 0
        print(parser.my_device.model)
        while switch_iterator < len(known_switches):
            if  parser.my_device.model[inventory_iterator] in known_switches[switch_iterator]:
                __print.my_print("It's a switch!!!!!", printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT)

                is_switch = True
                parser.my_device.deviceFunction = DevFunct.LAN
                break
            #endif
            switch_iterator += 1
            # endwhile
        inventory_iterator += 1

    if( not is_switch ):
        __print.my_print(("It's NOT a switch: %s!!!!!" % parser.my_device.model), printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT)

        return False
    #
    # read interface status from switch
    #
    interface_output = cmd(my_classes.CISCO_CMD_SHOW_INT_STATUS)

    parser.parse_show_interface(interface_output)
    #
    # read trunk informations from switch
    #
    my_classes.child.buffer = ""

    trunk_output = cmd(my_classes.CISCO_CMD_SHOW_INT_TRUNK)

    parser.parse_show_int_trunk(trunk_output)
    #
    # READ LLDP information
    #

    lldp_output = cmd(my_classes.CISCO_CMD_SHOW_LLDP_NEIGH)

    parser.parse_lldp_output(lldp_output)
    #
    # READ CDP information
    #
    #
    cdp_output = cmd(my_classes.CISCO_CMD_SHOW_CDP_NEIGH)

    __print.my_print("##########################################", printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT)
    parser.parse_show_cdp(cdp_output)
    __print.my_print("##########################################", printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT)


    #
    # READ CDP details information
    #
    #
    cdp_det_output = cmd(my_classes.CISCO_CMD_SHOW_CDP_NEIGH_DET)

    __print.my_print("##########################################", printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT)
    parser.parse_show_cdp_det(cdp_det_output)
    __print.my_print("##########################################", printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT)
    #
    # READ VLAN output
    #
    #

    vlan_output = cmd(my_classes.CISCO_CMD_SHOW_VLAN_BRIEF)

    __print.my_print("##########################################", printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT)

    __print.my_print(vlan_output, printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT)

    __print.my_print("##########################################", printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT)

    parser.parse_show_vlan_brief(vlan_output)

    #
    # READ VTP output
    #
    #

    vtp_output = cmd(my_classes.CISCO_CMD_SHOW_VTP_STATUS)

    __print.my_print("##########################################", printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT)

    __print.my_print(vtp_output, printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT)

    __print.my_print("##########################################", printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT)

    parser.parse_show_vtp_status(vtp_output)

    #
    # READ interface details output
    #
    #

    ip_interface_det_output = cmd(my_classes.CISCO_CMD_SHOW_IP_INTERFACE_DET)

    parser.parse_show_ip_interface_details(ip_interface_det_output)

    #
    # READ HSRP detials
    #
    #

    ip_interface_det_output = cmd(my_classes.CISCO_CMD_SHOW_STANDBY_BRIEF)

    parser.parse_show_standby_brief(ip_interface_det_output)


    #
    # READ power inline information
    # it may contain important info from AP's
    #
    my_classes.devices_list.append(parser.my_device)

    __print.my_print("<-End read information from switch->", printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT)

    return True


def read_inventory_information():
    import my_print
    import my_classes
    import cisco_parser

    __print = Print()
    global child

    #global my_classes.child
    my_classes.child.delaybeforesend = 1
    my_classes.child.delayafterread = 2
    my_classes.child.timeout = my_classes.COMMAND_TIMEOUT

    parser = cisco_parser.CiscoParser()
    parser.my_device = my_classes.SwitchClass()
    parser.my_device.VTP = VTPClass()
    parser.my_device.siteID = None
    parser.my_device.hostname = None
    parser.my_device.MGMTIPaddress = None
    parser.my_device.ports = [] # DeviceInterface list
    parser.my_device.deviceFunction = DevFunct.NULL
    parser.my_device.Location = None
    parser.my_device.model = [] # must be list
    parser.my_device.serial = [] # must be list
    parser.my_device.module = []
    parser.my_device.module_serial = []
    parser.my_device.deviceAction = DevAction.NULL
    parser.my_device.vlan_list = [] # VlanClass
    parser.my_device.neighbor_list = [] # NeighborEntry
    parser.my_device.helperaddresses = [] # list of IP addresses


    import my_print

    global child
    global device_prompt
    global prev_device_prompt

    _print = my_print.Print()

    current_prompt = ""
    is_switch = False



    #if my_classes.is_jumphostprompt(my_classes.get_prompt()):
        #raw_input("Press any key to continue...")
    #    print("It's a jumphost, exit!")
    #return False


    __print.my_print("->Start read inventory information->", printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT)
    my_classes.child.sendline(my_classes.NEWLINE_STR)
    current_prompt = ("%s%s" % (my_classes.child.before,my_classes.child.after))
    current_prompt = str.strip(current_prompt)
    # Set the terminal length to 0
    __response = cmd( my_classes.CISCO_CMD_TERM_LENG_INF )
    __print.my_print(__response, printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT)
    #
    # send enter
    #
    my_classes.child.sendline(my_classes.NEWLINE_STR)
    # waiting for command prompt
    try:
        my_classes.child.expect(my_classes.CISCO_COMMAND_PROMPT, timeout=my_classes.COMMAND_TIMEOUT)
        __response = ("%s"% (my_classes.child.before))
    except:
        __print.my_print("Command timed out, nothing to do. Continue.", printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT) # nothing to-do

    # print("<enter>%s<->%s</enter>" % (my_classes.child.before,my_classes.child.after))
    parser.my_device.hostname = __response.splitlines()
    parser.my_device.hostname = parser.my_device.hostname[len(parser.my_device.hostname)-1]
    parser.my_device.hostname = parser.my_device.hostname.strip()
    current_prompt = parser.my_device.hostname
    __print.my_print("HOSTNAME:::::::::>%s<" % (parser.my_device.hostname), printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT) # nothing to-do

    #
    # read inventory
    #
    my_classes.child.buffer = ""

    __response = ""
    # my_classes.child.send("show inventory")

    # try:
    #     my_classes.child.expect(my_classes.CISCO_COMMAND_PROMPT, timeout=my_classes.COMMAND_TIMEOUT)
    #     __response = ("%s%s"% (my_classes.child.before, my_classes.child.after))
    # except:
    #     __print.my_print("Command timed out, nothing to do. Continue.", printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT) # nothing to-do

    __response = cmd(my_classes.CISCO_CMD_SHOW_INV)
    print("<inventory>")
    print( __response )
    print("</inventory>")
    # __print.my_print(__response, printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT) # nothing to-do
    print("<open file here>")
    my_file = my_classes.create_and_open_outputfile( "%s%s"%(my_classes.output_file_directory, parser.my_device.hostname ))
    print("<write file here>")
    my_file.write(__response)
    print("</write file here>")


    my_classes.child.send(my_classes.NEWLINE_STR)
    my_classes.child.expect(my_classes.CISCO_COMMAND_PROMPT, my_classes.COMMAND_TIMEOUT)
    my_classes.child.sendline(my_classes.CISCO_CMD_EXIT)
    my_classes.child.expect(my_classes.CISCO_COMMAND_PROMPT, my_classes.COMMAND_TIMEOUT)

    print("%s%s"%(my_classes.child.before,my_classes.child.after))

    my_file.close()
    print("<close file here>")

    return True


def main():

    import my_print
    import my_classes

    __print = my_print.Print()
    is_switch = False

    __devices_IP_list = []
    #global my_classes.devices_list = [] # list of SwitchClass

    #global my_classes.child

    # create and open directory and files for output
    my_classes.prepare_outputfiles_dirs()

    failed_connections_file = my_classes.create_and_open_outputfile(failed_connections_filename)
    # generate output directory
    #my_classes.generate_output_dir()

    # login to JUMPHOST, which is the first jump, constant JUMPHOST_IP
    spawn_args = "%s -l %s %s" % (SSH_COMMAND_ON_SERVER, USERNAME_JUMPHOST, JUMPHOST_IP)

    __print.my_print(my_classes.SEPARATOR_STR, printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT)
    __print.my_print(spawn_args, printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT)
    __print.my_print(my_classes.SEPARATOR_STR, printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT)

    my_classes.child = pexpect.spawn( spawn_args , timeout=JUMPHOST_CONN_TIMEOUT)
    my_classes.child.delaybeforesend = 1.0
    fout = open(my_classes.EXPECT_OUTPUT_FILE, "wb")
    my_classes.child.logfile=fout

    try:
        # Wait for
        my_classes.child.expect('(?i)assword')
        # Wait for 'noecho' signal
        my_classes.child.waitnoecho(WAIT_NOECHO)
        # Send password
        my_classes.child.sendline(PASSWORD_JUMPHOST)
        # Wait for server prompt
        my_classes.child.expect(SERVER_PROMPT, JUMPHOST_TIMEOUT)
        # Send NEWLINE command
        my_classes.child.sendline(my_classes.NEWLINE_STR)
        my_classes.child.expect(SERVER_PROMPT)


    except pexpect.TIMEOUT:
        __print.my_print(('Connection timed out to %s' % (JUMPHOST_IP) ), printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT)
        sys.exit(1)
    except:
        __print.my_print(('Can not connect to %s' % (JUMPHOST_IP) ), printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT)
        __print.my_print(str(my_classes.child), printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT)
        sys.exit(1)

    __print.my_print(('Successfully connected to %s server.' % (JUMPHOST_IP) ), printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT)

    # Add prompt to
    my_classes.push_to_jumpstack(my_classes.get_prompt())

    # Login to the second jump host using constant JUMPHOST_IP_SWITCH and AAA user/pwd
    # IF not connect, then exit with error msg
    conn_jump_args = "%s -l %s %s" % (SSH_COMMAND_ON_SERVER, USERNAME_AAA, JUMPHOST_IP_SWITCH)

    __print.my_print(SEPARATOR_STR, printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT)
    __print.my_print(conn_jump_args, printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT)
    __print.my_print(SEPARATOR_STR, printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT)

    my_classes.child.sendline( conn_jump_args )

    try:
        # Wait for
        my_classes.child.expect('(?i)assword')
            # Wait for 'noecho' signal
        my_classes.child.waitnoecho(WAIT_NOECHO)
            # Send password
        my_classes.child.sendline(PASSWORD_AAA)
            # Wait for server prompt
        my_classes.child.expect(my_classes.CISCO_COMMAND_PROMPT, JUMPHOST_TIMEOUT)
            # Send custom command
        __print.my_print(("--------------------->%s<->%s<---------" % (my_classes.child.before,my_classes.child.after)), printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT)


    except pexpect.TIMEOUT:
        __print.my_print(('Connection timed out to %s' % (my_classes.child.before,my_classes.child.after)), printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT)
        sys.exit(1)
    except:
        __print.my_print('Can not connect to %s' % (JUMPHOST_IP_SWITCH), printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT)
        __print.my_print(str(my_classes.child), printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT)
        sys.exit(1)

    __print.my_print(('Successfully connected to %s server.' % (JUMPHOST_IP_SWITCH) ), printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT)
    my_classes.push_to_jumpstack(my_classes.get_prompt())

        ### active connection to server
            # Implement everything here if you want to use the first server as jump
        # Loading devices from file, one IP address in one line
    try:
        with open(my_classes.DEVICE_LIST_FILE, 'r') as fp:
                line = fp.readline()
                while line:
                    __devices_IP_list.append(str.strip(line))
                    line = fp.readline()
                    # close the file
        fp.close()
    except IOError as e:
        __print.my_print(('Can not open the file %s : %s' % (DEVICE_LIST_FILE, e.strerror)), printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT)
        sys.exit(1)

        # Go through on devices in a loop
    device_iterator = 0
    for list_item in __devices_IP_list:
        is_connected = False # Connection was uccessfully
        is_switch = False
        is_access_point = False

        device_iterator = device_iterator + 1
        __print.my_print(('Read information from %s -> %s address' % (device_iterator, list_item)), printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT)

        my_classes.child.sendline(my_classes.NEWLINE_STR)

        # Try to login using SSH and AAA user/pw
        if (connect_with_ssh( list_item, USERNAME_AAA, PASSWORD_AAA)) != None:
            is_connected = True
           #__print.my_print(('Connection to %s IP failed. Please make sure, it is available!' % list_item), printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT)
           #continue
        elif (connect_with_ssh( list_item, USERNAME_LOCAL, PASSWORD_LOCAL)) != None:
          is_connected = True

           # if it fail, then try to login using SSH and local/pw
        elif (connect_with_telnet( list_item, USERNAME_AAA, PASSWORD_AAA)) != None:
           # if it fail, then try to login using telnet and AAA user/pw
           is_connected = True
        elif (connect_with_telnet( list_item, USERNAME_LOCAL, PASSWORD_LOCAL)) != None:
           # if it fail, then try to login using telnet and local user/pw
           is_connected = True

           #
           # FOR ACCESS POINTS
           #
        #elif (connect_with_ssh( list_item, AP_USERNAME_NEW1, AP_PASSWORD_NEW1 )):
        #    is_connected = True
        #elif (connect_with_ssh( list_item, AP_USERNAME_OLD1, AP_PASSWORD_OLD1 )):
        #    is_connected = True
        #elif (connect_with_ssh( list_item, AP_USERNAME_OLD2, AP_PASSWORD_OLD2 )):
        #    is_connected = True
        #elif (connect_with_telnet( list_item, AP_USERNAME_NEW1, AP_PASSWORD_NEW1 )):
        #    is_connected = True
        #elif (connect_with_telnet( list_item, AP_USERNAME_OLD1, AP_PASSWORD_OLD1 )):
        #    is_connected = True
        #elif (connect_with_telnet( list_item, AP_USERNAME_OLD2, AP_PASSWORD_OLD2 )):
        #    is_connected = True
        else:
           # if no answer, then continue
            __print.my_print(('Connection to %s IP failed. Please make sure, it is available!' % list_item), printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT)
            failed_connections_file.write("Failed: %s\n" % list_item)
            continue
        # end wlif

        if is_connected:
            failed_connections_file.write("Connected: %s\n" % list_item)

            read_inventory_information()

            # should QUIT to jumphost before connecting to another device!!!!
            if not my_classes.is_jumphostprompt(my_classes.get_prompt()):
                #raw_input("Press any key to continue...")
                print("NOT a jumphost, exit!")
                my_classes.child.sendline(my_classes.CISCO_CMD_EXIT)
                my_classes.child.expect(my_classes.CISCO_COMMAND_PROMPT, SWITCH_CONN_TIMEOUT)
                print("%s%s" % (my_classes.child.before,my_classes.child.after))
                __print.my_print(("%s%s" % (my_classes.child.before,my_classes.child.after)), printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT)
            else:
                print("It's a jumphost prompt, nothing to do.")

    # Send 'exit' command to server

    __print.print_device_information(my_classes.devices_list)

    my_classes.close_outputfiles()
    failed_connections_file.close()
    sys.exit(0)
    return 0


if __name__ == "__main__":
    main()


# Read router informations
