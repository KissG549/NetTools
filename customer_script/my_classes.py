# datastructures and methods

from enum import Enum, unique
import io, os, sys, time, getopt
import signal, struct, constant
from cStringIO import StringIO
import string

import pexpect
#import my_print
# global variables

device_prompt = ''
prev_device_prompt = ''
child = pexpect.spawn
login_stack = []
jumphost_stack = []
devices_list = [] # list of SwitchClass


OUTPUT_FILE_DIRECTORY = "/home/littleg/Dokumentumok/DEVELOPMENT_DIR/customer_script/outputs/"
INVENTORY_OUTPUT_FILENAME_PREFIX = "inventory_"
CONNECTION_TABLE_OUTPUT_FILENAME_PREFIX = "connection_table_"
VTP_STATUS_OUTPUT_FILENAME_PREFIX = "vtpstatus_"
VLANS_OUTPUT_FILENAME_PREFIX = "vlans_"
CDP_OUTPUT_FILENAME_PREFIX = "cdp_"

INVENTORY_OUTPUT_FILENAME = "inventory"
CONNECTION_TABLE_OUTPUT_FILENAME = "connection_table"
VTP_STATUS_OUTPUT_FILENAME = "vtpstatus"
VLANS_OUTPUT_FILENAME = "vlans"
CDP_OUTPUT_FILENAME = "cdp"
IP_ADDR_OUTPUT_FILENAME = "ipaddr"
DEVINFOFORDRAW_FILENAME = "devinfofordrawing"

output_file_directory = OUTPUT_FILE_DIRECTORY
inventory_filename = INVENTORY_OUTPUT_FILENAME
connection_table_filename = CONNECTION_TABLE_OUTPUT_FILENAME
vtp_status_filename = VTP_STATUS_OUTPUT_FILENAME
vlans_filename = VLANS_OUTPUT_FILENAME
cdp_filename = CDP_OUTPUT_FILENAME
ip_addr_filename = IP_ADDR_OUTPUT_FILENAME
devinffordrawing_filename = DEVINFOFORDRAW_FILENAME

inventory_file = None
connection_table_file = None
vtp_status_file = None
vlans_file = None
cdp_file = None
ip_addr_file = None
devinffordrawing_file = None

known_switches = ["WS-C3560CX-12PC-S", "WS-C3650-24TS-S", "WS-C3650-48TS", "WS-C3850-12S", "WS-C3850-12XS-S", "WS-C3850-24T", "WS-C3850-48T", "WS-C3650-24PS-S", "WS-C3650-48PS-S", "WS-C3650-48FS-S", "WS-C3850-24P-S", "WS-C3850-48P-S", "WS-C2924M-XL-A", "WS-C2940-8TT-S",  "WS-C2950-12", "WS-C2950-24", "WS-C2950C-24", "WS-C2950G-24-EI", "WS-C2950SX-24", "WS-C2950SX-48-SI", "WS-C2950T-24", "WS-C2950T-48-SI", "WS-C2960-24LC-S", "WS-C2960-24LT-L", "WS-C2960-24PC-L", "WS-C2960-24PC-S", "WS-C2960-24-S", "WS-C2960-24TC-L", "WS-C2960-24TC-S", "WS-C2960-24TT-L", "WS-C2960-48PST-L", "WS-C2960-48PST-S", "WS-C2960-48TC-L", "WS-C2960-48TC-S", "WS-C2960-48TT-L", "WS-C2960-8TC-L", "WS-C2960-8TC-S", "WS-C2960CG-8TC-L", "WS-C2960G-24TC-L", "WS-C2960G-48TC-L", "WS-C2960G-8TC-L", "WS-C2960S-24PS-L", "WS-C2960S-24TS-L", "WS-C2960S-24TS-S", "WS-C2960S-48FPS-L", "WS-C2960S-48LPS-L", "WS-C2960S-48TS-L", "WS-C2960S-48TS-S", "WS-C2960S-F24PS-L", "WS-C2960S-F48FPS-L", "WS-C3508G-XL-EN", "WS-C2960X-24PS-L", "WS-C2960CX-8PC-L", "WS-C2960C-12PC-L", "WS-C2960X-24PS-L", "WS-C2960X-48LPS-L", "WS-C2960X-48FPS-L", "WS-C3550-48-SMI", "WS-C3560-12PC-S", "WS-C3560-24PS-E", "WS-C3560-24PS-S", "WS-C3560-24TS-S", "WS-C3560-48PS-E", "WS-C3560-48PS-S", "WS-C3560-48TS-E", "WS-C3560-48TS-S", "WS-C3560-8PC-S", "WS-C3560CG-8PC-S", "WS-C3560G-24PS-S", "WS-C3560G-24TS-E", "WS-C3560G-24TS-S", "WS-C3560G-24TS-S", "WS-C3560G-48PS-E", "WS-C3560V2-24PS-S", "WS-C3560V2-48PS-S", "WS-C3560X-24P-S", "WS-C3560X-24T-S", "WS-C3560X-48PF-S", "WS-C3750-24PS-S", "WS-C3750-24TS-E", "WS-C3750-48PS-S", "WS-C3750-48TS-S", "WS-C3750E-24PD-S", "WS-C3750E-24TD-E", "WS-C3750E-24TD-S", "WS-C3750E-48PD-SF", "WS-C3750G-12S-E", "WS-C3750G-12S-S", "WS-C3750G-24PS-E", "WS-C3750G-24PS-S", "WS-C3750G-24T-E", "WS-C3750G-24T-S", "WS-C3750G-24TS-E", "WS-C3750G-24TS-E1U", "WS-C3750G-24TS-S", "WS-C3750G-24TS-S1U", "WS-C3750G-24WS-S25", "WS-C3750G-48PS-S", "WS-C3750V2-24PS-S", "WS-C3750V2-48PS-E", "WS-C3750V2-48PS-S", "WS-C3750X-12S-E", "WS-C3750X-12S-S", "WS-C3750X-24P-L", "WS-C3750X-24P-S", "WS-C3750X-24S-E", "WS-C3750X-24S-S", "WS-C3750X-24S-S", "WS-C3750X-24T-L", "WS-C3750X-24T-S", "WS-C3750X-48P-E", "WS-C3750X-48P-L", "WS-C3750X-48P-S", "WS-C3750X-48T-L", "WS-C3750X-48T-S", "WS-C4506", "WS-C4507R", "WS-C4507R-E", "WS-C4948-10GE", "WS-C6513"]

known_access_points = ["AIR-LAP1041N-E-K9", "AIR-LAP1042N-A-K9", "AIR-LAP1042N-E-K9", "AIR-AP1042N-E-K9", "AIR-AP1121G-E-K9", "AIR-AP1131AG-E-K9", "AIR-AP1131G-E-K9", "AIR-LAP1131AG-E-K9", "AIR-LAP1131G-E-K9", "AIR-LAP1141N-E-K9", "AIR-AP1141N-E-K9", "AIR-LAP1142N-E-K9", "AIR-AP1142N-E-K9", "AIR-AP1220-IOS-UPGRD", "AIR-AP1230B-E-K9", "AIR-AP1231G-E-K9", "AIR-LAP1231G-E-K9", "AIR-AP1242AG-E-K9", "AIR-AP1242G-E-K9", "AIR-LAP1242AG-E-K9", "AIR-LAP1242G-E-K9", "AIR-LAP1262N-E-K9", "AIR-AP1262N-E-K9", "AIR-AP1572EAC-E-K9", "AIR-AP1832I-E-K9", "AIR-AP1852I-E-K9", "AIR-AP2702E-UXK9", "AIR-AP350", "AIR-CAP1532E-E-K9", "AIR-CAP1552H-E-K9", "AIR-CAP1602E-E-K9", "AIR-CAP1602I-E-K9", "AIR-LAP1602E-E-K9", "AIR-LAP1602I-E-K9", "AIR-SAP1602E-E-K9", "AIR-SAP1602I-E-K9", "AIR-CAP1702I-E-K9", "AIR-SAP1702I-E-K9", "AIR-CAP2602E-E-K9", "AIR-CAP2602I-E-K9", "AIR-SAP2602E-E-K9", "AIR-SAP2602I-E-K9", "AIR-CAP2702E-E-K9", "AIR-CAP2702I-E-K9", "AIR-SAP2702E-E-K9", "AIR-SAP2702I-E-K9", "AIR-CAP3602E-E-K9", "AIR-CAP3702E-E-K9", "AIR-CAP702I-E-K9", "AIR-LAP1252AG-E-K9", "AIR-LAP1261N-E-K9"]

# Simple outputs
LOGFILE = "/home/littleg/Dokumentumok/DEVELOPMENT_DIR/customer_script/cisco_script.log"

EXPECT_OUTPUT_FILE = "/home/littleg/Dokumentumok/DEVELOPMENT_DIR/customer_script/my_pexpect.log"
# Usable output for datasource
OUTPUT_FILE = "/home/littleg/Dokumentumok/DEVELOPMENT_DIR/customer_script/cisco_script_output.log"

DIRECTORY_SEPARATOR = "/"
#
#   Constants for datasource
#
#

SSH_NEWKEY = 'Are you sure you want to continue connecting (yes/no)?'

DEVICE_LIST_FILE = "/home/littleg/Dokumentumok/DEVELOPMENT_DIR/customer_script/devices.txt"


###
#   Login credentials
#

USERNAME_JUMPHOST = 'myuserid'
#USERNAME_JUMPHOST = 'littleg'

PASSWORD_JUMPHOST = 'password1'
#PASSWORD_JUMPHOST = 'password2'

USERNAME_AAA = 'myuser'

PASSWORD_AAA = 'password3'

USERNAME_LOCAL = 'l_user'

PASSWORD_LOCAL = 'password'

AP_USERNAME_OLD1 = 'user'

AP_PASSWORD_OLD1 = 'password'

AP_USERNAME_OLD2 = 'user'

AP_PASSWORD_OLD2 = 'password'

AP_USERNAME_NEW1 = 'user'

AP_PASSWORD_NEW1 = 'password'

# Name of the SSH client program, it could be also URL
#
SSH_COMMAND_ON_SERVER = 'ssh -o StrictHostKeyChecking=no'

SSH_COMMAND_ON_CISCO = 'ssh'

TELNET_COMMAND = 'telnet'
#
# Prompt definitions
#

SERVER_PROMPT = '\$.*'
# Prompt
COMMAND_PROMPT = '[#$] '

CISCO_COMMAND_PROMPT = '[>#]'

JUMPHOST_PROMPT = '[myuserid@jumphost1.*'

JUMPHOST_PROMPT = 'jumphost2.*'

SWITCH_PROMPT = '.-sw-.'

ROUTER_PROMPT = '.-r-.'

AP_PROMPT = '.-ap-.'
# DEVICE IP address
# JUMPHOST_IP, can jump directly to routers
JUMPHOST_IP = '10.10.10.1'
# JUMPHOST_IP = '127.0.0.1'

# JUMPHOST_IP_SWITCH - HUN
JUMPHOST_IP_SWITCH = '10.10.10.2'

#
# Timeouts in sec
#
JUMPHOST_CONN_TIMEOUT = 10

JUMPHOST_TIMEOUT = 10

COMMAND_TIMEOUT = 30

CONN_TIMEOUT = 30

SWITCH_CONN_TIMEOUT = 30

ROUTER_TIMEOUT = 10

WAIT_NOECHO = 10

# Seconds for sleeping before the prompt, expect does not wait until the appropriate time
# i have to manage it myself
SLEEP_BEFORE_CISCO_PROMPT = 8


# Commands

NEWLINE_STR = '\x0d'

CISCO_CMD_TERM_LENG_INF = 'term leng 0'
CISCO_CMD_SHOW_INV = 'show inventory'
CISCO_CMD_SHOW_INT_STATUS = 'show int status'
CISCO_CMD_SHOW_INT_TRUNK = 'show int trunk'
CISCO_CMD_SHOW_LLDP_NEIGH = 'show lldp neighbors'
CISCO_CMD_SHOW_CDP_NEIGH = 'show cdp neighbors'
CISCO_CMD_SHOW_CDP_NEIGH_DET = 'show cdp neighbors detail'
CISCO_CMD_SHOW_VLAN_BRIEF = 'show vlan brief'
CISCO_CMD_SHOW_VTP_STATUS = 'show vtp status'
CISCO_CMD_SHOW_INTERFACE_DET = 'show interface'
CISCO_CMD_SHOW_IP_INTERFACE_DET = 'show ip interface'
CISCO_CMD_SHOW_IP_INTERFACE_BRIEF = 'show ip interface brief'
CISCO_CMD_SHOW_STANDBY_BRIEF = 'show standby brief'
CISCO_CMD_SHOW_VERSION = 'show version'
CISCO_CMD_EXIT = 'exit'

SEPARATOR_STR = "------------------------------"
SPEC_SEPARATOR ="########################################"

TWOMETER_STR = "2m"
TRUNKTWOMETER_STR = "2x2 m"

DEVICE_ID_NUMCHARS = 16
LOCAL_INT_NUMCHARS = 18
HOLDTIME_NUMCHARS = 11
CAPABILITY_NUMCHARS = 10
PLATFORM_NUMCHARS = 10
PORT_ID_NUMCHARS = 8
REMOTE_PORT_NUMCHARS = 68

ACCESS_STR = "access"
TRUNK_STR = "trunk"

STATE_UP_STR = "UP"
STATE_SHUTDOWN_STR = "SHUTDOWN"

NOT_AVAILABLE_DATA_STR = "N/A"
MISSING_DATA_STR = "-"
TRUNK_PORT_STR ="Trunk port"
ACCESS_PORT_STR = "Access port"
GENERAL_PORT_STR = "Eth0"
NOT_CONNECTED_STR = "Not connected"

CONNECTED_STR = "connected"
NOTCONNECTED_STR = "notconnect"
DISABLED_STR = "disabled"
ERRDISABLED_STR = "err-disabled"

RJ45_STR = "TX"
RJ45_NAME_STR = "RJ45"
GLCT_STR = "TX-SFP"
GLCT_MODULENAME_STR = "GLC-T"
GLCSXMMD_STR = "SX-SFP"
GLCSX_MODULENAME_STR = "GLC-SX-MMD="
GLCLHSMD_STR = "LH-SFP"
GLCLHSMD_MODULENAME_STR = "GLC-LH-SMD="
NOTPRESENT_STR = "NotPresent"
OTHER_STR = "other"

UTP_STR = "Cat5e/Cat6   UTP"
LCtoLCMM_STR = "Fiber patchcord - LC to LC - Multi Mode"
LCtoLCSM_STR = "Fiber patchcord - LC to LC - Single Mode"


VTP_MODE_CLIENT_STR = "Client"
VTP_MODE_SERVER_STR = "Server"
VTP_MODE_TRANSPARENT_STR = "Transparent"
VTP_MODE_NEW_STR = "Transparent"

VTP_STR = "VTP"
DOMAIN_STR = "Domain"
OPERATING_STR = "Operating"

CDP_DEVICE_ID_STR = "Device ID:"
CDP_IP_ADDRESS_STR = "IP address:"
CDP_PLATFORM_STR = "Platform:"
CDP_INTERFACE_ID_STR = "Interface:"
CDP_PORT_ID_STR = "Port ID"
CDP_OUTGOING_PORT_STR = "outgoing port"
CDP_ENTRY_SEPARATOR_STR = "-------------------------"

VLAN_NATIVE_STR = "Native"
VLAN_ALLOWED_STR = "allowed"
PORT_STR = "Port"

LINE_PROTO_STR = "line protocol"
INT_ADMINISTRATIVELY_STR = "administratively"
INT_DESCRIPTION_STR = "Description"
INT_INTERNET_STR = "Internet"
INT_DISABLED_STR = "disabled"
INT_HELPER_STR= "Helper"
INT_SECONDARY_STR = "Secondary address"
INT_INTERFACE_STR = "Interface"
INT_UNASSIGNED_STR = "unassigned"

INT_INTERFACE_ID = 0
INT_IPADDR_ID = 1
INT_OK_ID = 2
INT_STATUS_ID = 3
INT_PROTOCOL_ID = 4

INT_OK_YES_STR = "YES"

HSRP_INTERFACE_ITEM_ID = 0
HSRP_GROUP_ID = 1
HSRP_PRIO_ID = 2
HSRP_STATE_ID = 4
HSRP_ACTIVE_ID = 5
HSRP_STANDBY_ID = 6
HSRP_VIRTUAL_ID = 7
HSRP_MAX_ITEMS_IN_LINE = 8

VERSION_SOFTWARE_STR = "Software"
AP_LEIGHTWEIGHT_SIGN_STR = "W8"
AP_LEIGHTWEIGHT_STR = "LeightWeightAP"
AP_NOT_LEIGHTWEIGHT_STR = "NOT_LeightWeightAP"

def prepare_outputfiles_dirs():
    global output_file_directory
    global inventory_filename
    global connection_table_filename
    global vtp_status_filename
    global vlans_filename
    global cdp_filename
    global ip_addr_filename
    global devinffordrawing_filename

    global inventory_file
    global connection_table_file
    global vtp_status_file
    global vlans_file
    global cdp_file
    global ip_addr_file
    global devinffordrawing_file

    # create the directory if not exist and the subdirectory
    output_file_directory = generate_output_dir(output_file_directory)

    if output_file_directory[:-1] != DIRECTORY_SEPARATOR:
        output_file_directory += DIRECTORY_SEPARATOR

    inventory_file = create_and_open_outputfile( "%s%s"%(output_file_directory,inventory_filename ))
    connection_table_file = create_and_open_outputfile( "%s%s"%(output_file_directory,connection_table_filename ))
    vtp_status_file = create_and_open_outputfile( "%s%s"%(output_file_directory,vtp_status_filename ))
    vlans_file = create_and_open_outputfile( "%s%s"%(output_file_directory,vlans_filename ))
    cdp_file = create_and_open_outputfile( "%s%s"%(output_file_directory,cdp_filename ))
    ip_addr_file = create_and_open_outputfile( "%s%s"%(output_file_directory,ip_addr_filename ))
    devinffordrawing_file = create_and_open_outputfile( "%s%s"%(output_file_directory,devinffordrawing_filename ))
    #create and open files

    return

# end prepare_outputfiles_dirs

def close_outputfiles():
    inventory_file.close()
    connection_table_file.close()
    vtp_status_file.close()
    vlans_file.close()
    cdp_file.close()
    ip_addr_file.close()
    devinffordrawing_file.close()
    return
# end close_outputfiles

def generate_output_dir( directory = OUTPUT_FILE_DIRECTORY ):
    import my_print
    import time
    timestr = time.strftime("%Y%m%d-%H%M%S")

    outputpath = directory
    outputpath += DIRECTORY_SEPARATOR
    outputpath += timestr
    _print = my_print.Print()

    try:
        os.mkdir(outputpath)
    except OSError:
        _print.my_print("Creation of the directory %s failed" % outputpath)
        return None
    else:
        _print.my_print("Successfully created the directory %s " % outputpath)
    return outputpath

def create_and_open_outputfile( filename = "default" ):
    import time
    #timestr = time.strftime("%Y%m%d-%H%M%S")
    #filename = prefix + timestr
    try:
        file = open( filename, "a+")
    except:
        _print.my_print("Can't create the file %s" % filename )
        return False
    return file

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

def remove_whitespaces( my_text ):
    __text = str.strip(my_text)
    return __text

def remove_empty_lines( my_text ):
    clear_line = []
    for line in my_text:
        if not line.strip():
            continue
        else:
            clear_line.append(my_text)
    return clear_line

def get_last_line( my_text ):
    # create new string
    lastline = str()
    # split line into a list
    lastline = my_text.splitlines()
    # get the last item
    lastline = lastline[len(lastline)-1]
    # remove whitespaces
    lastline = lastline.strip()
    return lastline

def push_to_loginstack(current_prompt):
    return login_stack.append(current_prompt)

def pop_login_stack():
    return login_stack.pop()

def push_to_jumpstack(jumphost_prompt):
    return jumphost_stack.append(jumphost_prompt)

def pop_jumpstack():
    return jumphost_stack.pop()

def is_jumphostprompt(current_prompt):

    prompt_iterator = 0

    while prompt_iterator < len(jumphost_stack):
        if current_prompt == jumphost_stack[prompt_iterator]:
            return True
        # endif
        prompt_iterator+=1
    # endwhile
    return False

def get_prompt():

    import my_print

    __print = my_print.Print()
    __hostname = ""
    __response = ""
    # send new line
    time.sleep(0.1)
    child.sendline(NEWLINE_STR)
    # waiting for command prompt
    try:
        child.expect(CISCO_COMMAND_PROMPT, timeout=COMMAND_TIMEOUT)
    except:
        __print.my_print("Command timed out, nothing to do. Continue.", printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT) # nothing to-do

    #
    # Get the hostname here and print
    #
    __response = ("RESPONSE:>%s<"% (child.before))

    __hostname = __response.splitlines()
    print("RESPONSE:>%s<"% (child.before))
    print("HOSTNAME------>%s<"% __response)
    print("")
    __hostname = __hostname[len(__hostname)-1]
    __hostname = __hostname.strip()
    __print.my_print("HOSTNAME:::::::::>%s<" % (__hostname), printlevel_loc = my_print.PrintLevel.DEBUG, printdestination_loc = my_print.PrintDestination.STDOUT) # nothing to-do

    return __hostname

def cmd( my_command):
    import my_print

    _print = my_print.Print()
    global child
    child.delaybeforesend = 1
    child.delayafterread = 1
    child.timeout = COMMAND_TIMEOUT
    response = str()
    current_prompt = str()
    bytes = 0
    curr_bytes = 0
    command_end_sign_num = 5

    __not_used_var = child.before
    __not_used_var = child.after

    child.buffer = ""
    child.sendline(NEWLINE_STR)

    try:
        child.expect(CISCO_COMMAND_PROMPT, timeout=COMMAND_TIMEOUT)
        current_prompt = ("%s%s" % (child.before,child.after))
        current_prompt =get_last_line(current_prompt)
        _print.my_print(current_prompt)
        print("HOSTNAME:>%s<"%current_prompt)
    except:
        _print.my_print("Timed out, nothing to do. Continue.") # nothing to-do

    child.sendline(my_command)

    try:
        while True:
            #print("Start while loop")
            my_string = str()
            my_string = child.read_nonblocking(size = 1024,timeout=1)
            curr_bytes = len(my_string)
            response = ("%s%s" % (response,my_string))
            bytes += curr_bytes
            #print("---->%s<>%s<----" % (response,my_string) )
                # print("READ: ", my_string)
            if ((response.count(current_prompt) > 5 )):
                #print("Prompt is in the answer!!!!!!!!!!!!!!!!!!!!!!")
                    #   print("This is EOF")
                break
            elif curr_bytes < 1:
                __not_used_var = "" # do nothing
                #break
            # endif
            #print("END while loop")


        #endwhile
    except:
        _print.my_print("Timed out, nothing to do. Continue.") # nothing to-do

    __not_used_var = child.before
    __not_used_var = child.after

    return response


def connect_with_ssh( __host, __user, __pwd ):
    import my_print

    global child
    global device_prompt
    global prev_device_prompt

    _print = my_print.Print()

    conn_args = "%s -l %s %s" % (SSH_COMMAND_ON_CISCO, __user, __host)

    _print.my_print(SEPARATOR_STR)
    _print.my_print(conn_args)
    _print.my_print(SEPARATOR_STR)
    global child
    child.sendline( conn_args )

    try:
        # Wait for
        child.expect('[Pp]assword')
        # Wait for 'noecho' signal
        child.waitnoecho(WAIT_NOECHO)
        # Send password
        child.sendline(__pwd)
        # Wait for server prompt
        child.expect(CISCO_COMMAND_PROMPT, SWITCH_CONN_TIMEOUT)
        _print.my_print("--------------------->%s<->%s<---------" % (child.before,child.after), printlevel_loc = my_print.PrintLevel.INFORMATION, printdestination_loc = my_print.PrintDestination.STDOUT)
        time.sleep(0.1)
        # Wait for server prompt
        child.sendline(NEWLINE_STR)
        child.expect(CISCO_COMMAND_PROMPT)

        #add_prompt_to_stack( "%s%s" % (child.before, child.after))

    except pexpect.TIMEOUT:
        _print.my_print(("Connection timed out to %s" % (__host) ), printlevel_loc = my_print.PrintLevel.INFORMATION, printdestination_loc = my_print.PrintDestination.STDOUT)
        child.sendline('\x03')
        child.sendline(NEWLINE_STR)

        return None
    except:
        _print.my_print(("Can not connect to  %s" % (__host) ), printlevel_loc = my_print.PrintLevel.INFORMATION, printdestination_loc = my_print.PrintDestination.STDOUT)
        _print.my_print(str(child), printlevel_loc = my_print.PrintLevel.INFORMATION, printdestination_loc = my_print.PrintDestination.STDOUT)
        child.sendline('\x03')
        child.sendline(NEWLINE_STR)
        return None

    _print.my_print('Successfully connected to %s' % (__host), printlevel_loc = my_print.PrintLevel.INFORMATION, printdestination_loc = my_print.PrintDestination.STDOUT)
    time.sleep(0.1)
    return child
# end connect_with_ssh

def connect_with_telnet( __host, __user, __pwd ):
    import my_print

    global child
    global device_prompt
    global prev_device_prompt

    _print = my_print.Print()

    conn_args = "%s %s" % (TELNET_COMMAND, __host)

    _print.my_print(SEPARATOR_STR)
    _print.my_print(conn_args)
    _print.my_print(SEPARATOR_STR)

    child.sendline( conn_args )

    try:
        # Wait for
        child.expect('(?)username')
        child.sendline(__user)
        child.expect('(?i)assword')
        # Wait for 'noecho' signal
        time.sleep(0.5)
        # Send password
        child.sendline(__pwd)
        # Wait for server prompt
        child.expect(CISCO_COMMAND_PROMPT, SWITCH_CONN_TIMEOUT)
        _print.my_print("--------------------->%s<->%s<---------" % (child.before,child.after), printlevel_loc = my_print.PrintLevel.INFORMATION, printdestination_loc = my_print.PrintDestination.STDOUT)
        time.sleep(0.1)
        # Wait for server prompt
        child.sendline(NEWLINE_STR)
        child.expect(CISCO_COMMAND_PROMPT)

        #add_prompt_to_stack( "%s%s" % (child.before, child.after))

    except pexpect.TIMEOUT:
        _print.my_print(("Connection timed out to %s" % (__host) ), printlevel_loc = my_print.PrintLevel.INFORMATION, printdestination_loc = my_print.PrintDestination.STDOUT)
        child.sendline('\x03')
        child.sendline(NEWLINE_STR)
        return None
    except:
        _print.my_print(("Can not connect to  %s" % (__host) ), printlevel_loc = my_print.PrintLevel.INFORMATION, printdestination_loc = my_print.PrintDestination.STDOUT)
        #_print.my_print(str(child), printlevel_loc = my_print.PrintLevel.INFORMATION, printdestination_loc = my_print.PrintDestination.STDOUT)
        child.sendline('\x03')
        child.sendline(NEWLINE_STR)
        return None

    _print.my_print('Successfully connected to %s' % (__host), printlevel_loc = my_print.PrintLevel.INFORMATION, printdestination_loc = my_print.PrintDestination.STDOUT)
    time.sleep(0.1)
    return child
# end connect_with_ssh

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

class DeviceInterface:
    def __init__(self):
        interfacename = str()    # Name of the interface e.g.: GigabitEthernet 1/0/1 or Gig1/0/1
        interfacedescription = str() # Description from port configuration
        interfacetype = str()  # PortType RJ45, GLC-T, GLC-SX, GLC-LH
        allowedvlans = [] # list of allowed vlans
        accessvlan = str()
        voicevlan = str()
        nativevlan = str()
        status = str()  # connected/notconnected/disabled/err-disabled
        isvirtual = None # True when it's VLAN interface
        IPaddress = None # IP address or list of IP addresses, if it's a L3 interface
        netmask = [] # Netmask's for IP addresses
        neighborname = []
        neighborport = str()
        neighboripaddress = str()
        helperaddresses = [] # list of helper IP's
        hsrpactivenodeaddresses = ""
    # enddef

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
    helperaddresses = [] # list of helper IP's
    hsrpaddresses = ""
    hsrpactivenodeaddresses = ""

class VlanClass:
    def __init__(self):
        self.name = None
        self.number = None
        self.state = None
        self.enabled = None

    number = None
    name = None
    state = None
    enabled = None

class VTPModes(Enum):
    NULL = None
    VTP_MODE_CLIENT = "Client"
    VTP_MODE_SERVER = "Server"
    VTP_MODE_TRANSPARENT = "Transparent"

class NeighborEntry:
    device_id = None # Hostname or IP from LLDP or CDP
    address = None # IP address
    mgmt_address = None # MGMT IP address
    local_port = None # Where the remote device is conncted on this ( local )
    remote_port = None # The remote port of the connecion
    platform = None # Platform e.g: cisco WS-C2960G-24TC-L

class PrintLevel(Enum):
    NULL = 0
    INFORMATION = 1
    DEBUG = 2

class PrintDestination(Enum):
    NULL = None
    STDOUT = 1
    LOGFILE = 2
    ALL = 3


class VTPClass:
    VTPMode = None
    VTPDomain = None

class GeneralDevice(object):
    """ Class for store data of general device """
    def __init__(self):
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
    def is_switch(self):
        import my_print
        global known_switches

        _print.my_print( self.model )
        _print.my_print(known_switches)
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
        import my_print
        inventory_iterator = 0
        while inventory_iterator < len(self.model):
            ap_iterator = 0
            while ap_iterator < len(known_access_points):
                if  self.model[inventory_iterator] in known_access_points[ap_iterator]:
                    _print.my_print("It's an ap!!!!!")
                    return True
                #endif
                ap_iterator += 1
            # endwhile
            inventory_iterator += 1
        # endewhile
        return False
    #enddef



class SwitchClass(GeneralDevice):
    def __init__(self):
        VTP = VTPClass()
        isitstack = None

    VTP = VTPClass()
    isitstack = None

class AccessPointClass(GeneralDevice):

    is_leightweight = None
