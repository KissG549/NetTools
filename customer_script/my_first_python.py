#!/usr/bin/env python

from __future__ import print_function

from __future__ import absolute_import

import io, os, sys, time, getopt
import signal, struct, constant
import pexpect
import re # for filter

import general_device
from general_device import *

import logging
#
# Globals
#

device_prompt = ''
prev_device_prompt = ''
child = pexpect.spawn
login_stack = []
devices_l = []

output_file = None

#
# constants
#
SSH_NEWKEY = 'Are you sure you want to continue connecting (yes/no)?'

#
#   File names
#


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

USERNAME_LOCAL = ' '

PASSWORD_LOCAL = ' '

# Name of the SSH client program, it could be also URL
#
SSH_COMMAND_ON_SERVER = 'ssh -o StrictHostKeyChecking=no'

SSH_COMMAND_ON_CISCO = 'ssh'
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

COMMAND_TIMEOUT = 20

CONN_TIMEOUT = 30

SWITCH_CONN_TIMEOUT = 10

ROUTER_TIMEOUT = 10

WAIT_NOECHO = 10

# Seconds for sleeping before the prompt, expect does not wait until the appropriate time
# i have to manage it myself
SLEEP_BEFORE_CISCO_PROMPT = 8

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
    #text = my_text
    #print( text.splitlines() )
    #print( "qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq")
    #print( len(text) )
    #print( "qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq")
    #ret = __text.pop()
    #ret = my_text
    print("Please implement get_last_line( my_text )")
    ret = my_text
    return ret

def clear_login_prompt(my_line):
    my_line = remove_whitespaces(my_line)
    my_line = remove_empty_lines(my_line)
    return get_last_line(my_line)

def print_login_stack():
    global login_stack

    for stack_iterator in range(len(login_stack)):
            print(">>>%s<<<" % login_stack[stack_iterator])
    return

def is_it_in_login_stack( __login_prompt ):
    ret = False
    global login_stack
    #print ("Check login_stack for this item: %s" % __login_prompt )
    for stack_iterator in range(len(login_stack)):
        #print("->>>>>>>%s<<<<<<->>>%s<<<-" % (login_stack[stack_iterator], __login_prompt))

        if __login_prompt == login_stack[stack_iterator]:
            #print("They are equal")
            # stack_iterator = stack_iterator+1
            return True
        #print("They are different")
    return False

def add_prompt_to_stack( __login_prompt ):
    global login_stack

    __loc__prompt = clear_login_prompt( __login_prompt )
    #__loc__prompt = filter(lambda x: not re.match(r'^\s*$', x'), __loc__prompt)
    #print( "prompt: ->>%s<<-" % __login_prompt )

    if is_it_in_login_stack( __loc__prompt ):
        #print("It is already in the stack------------------------------------------------")
        return False
    else:
        #print("It is not in the stack, I will add it ------------------------------------------------")
        login_stack.append( __loc__prompt )
        #print("Login stack size: %s" % len(login_stack))
        #print_login_stack()
    return True

def remove_prompt_from_stack( __login_prompt ):
    global login_stack
    __loc__prompt = str.strip( __login_prompt )

    stack_iterator = 0
    while stack_iterator < len(login_stack):
        if __login_prompt == login_stack[stack_iterator]:
            login_stack.pop(stack_iterator)
            stack_iterator = stack_iterator + 1
    return False
# Login into the device with SSH, parameters: user, pw
# Return with pexpect object, or if it fails return with None

def cmd( my_command):
    logging.basicConfig(filename = general_device.DEBUG_LOGFILE, level=logging.DEBUG)
    global child
    child.delaybeforesend = 1
    child.delayafterread = 2
    child.timeout = COMMAND_TIMEOUT
    global child
    response = ""
    current_prompt = ""
    bytes = 0
    curr_bytes = 0
	#child.response = ""
    child.buffer = ""
    command_end_sign_num = 5

    child.sendline('\x0d')
    child.expect(CISCO_COMMAND_PROMPT, timeout=COMMAND_TIMEOUT)
    __hostname = ("%s%s" % (child.before,child.after))
    print(__hostname)
    logging.info(__hostname)

    child.sendline(my_command)

    try:
         child.expect(pexpect.EOF, timeout=COMMAND_TIMEOUT)
    except:
        print("Timed out, nothing to do. Continue.") # nothing to-do
        logging.info("Timed out, nothing to do. Continue.")

    response =("%s%s" % (child.before, child.after))

    return response

    while command_end_sign_num > 0:
        child.sendline('\x0d')
        command_end_sign_num -= 1
    # endwhile
    try:
        while True:
            my_string = 0
            my_string = child.read_nonblocking(size = 100,timeout=COMMAND_TIMEOUT)
            curr_bytes = len(my_string)
            response += my_string
            bytes += curr_bytes
                # print("READ: ", my_string)
            if ((my_string == pexpect.EOF) or
                (response.count(current_prompt) > command_end_sign_num )):
                    #   print("This is EOF")
                    break
            elif curr_bytes < 1:
                break
            # endif
        #endwhile
    except:
        print("Timed out, nothing to do. Continue.") # nothing to-do
        logging.info("Timed out, nothing to do. Continue.")

    child.expect(CISCO_COMMAND_PROMPT, SWITCH_CONN_TIMEOUT)

    return response


def connect_with_ssh( __host, __user, __pwd ):
    global child
    global device_prompt
    global prev_device_prompt

    conn_args = "%s -l %s %s" % (SSH_COMMAND_ON_CISCO, __user, __host)

    print('---')
    print(conn_args)
    print('---')
    global child
    child.sendline( conn_args )

    try:
        # Wait for
        child.expect('(?i)assword')
        # Wait for 'noecho' signal
        child.waitnoecho(WAIT_NOECHO)
        # Send password
        child.sendline(__pwd)
        # Wait for server prompt
        child.expect(CISCO_COMMAND_PROMPT, SWITCH_CONN_TIMEOUT)
        print("--------------------->%s<->%s<---------" % (child.before,child.after))
        time.sleep(0.1)
        # Wait for server prompt
        child.sendline('\x0d')
        child.expect(CISCO_COMMAND_PROMPT)

        add_prompt_to_stack( "%s%s" % (child.before, child.after))
        #mystring = str.strip(child.before)
        #print("--------------------->%s<---------" % (mystring))

    except pexpect.TIMEOUT:
        print ('Connection timed out to %s' % (__host) )
        sys.exit(1)
    except:
        print('Can not connect to %s' % (__host) )
        print(str(child))
        sys.exit(1)

    print('Successfully connected to %s' % (__host) )
    time.sleep(0.1)
    return child

# Login into the device with telnet, parameters: user, pw
# Return value: if ok -> true, if not -> false
def connect_with_telnet( __host, __user, __pwd ):
    ret = false
    print("Please implement function connect_with_telnet( __host, __user, __pwd ):!!!")

    return ret

def print_information_switch():

    global output_file

    if output_file == "":
        output_file = open(general_device.OUTPUT_FILE, "wb")

    device_iterator = 0
    curr_round = 0
    MAX_ROUND = 5 # number of parameters
    curr_device = SwitchClass()

    while device_iterator < len(devices_l):

        if curr_round == 0:
            print("<datasource_inventory>")
            output_file.write("<datasource_inventory>\r\n")
            devices_l[device_iterator].print_datasource_inventory(output_file)
            print("</datasource_inventory>")
            output_file.write("</datasource_inventory>\r\n")

        elif curr_round == 1:
            print("<datasource_connections>")
            output_file.write("<datasource_connections>\r\n")
            devices_l[device_iterator].print_datasource_connections(output_file)
            print("</datasource_connections>")
            output_file.write("</datasource_connections>\r\n")
        elif curr_round == 2:
            print("<datasource_vtp>")
            output_file.write("<datasource_vtp>\r\n")
            devices_l[device_iterator].print_datasource_vtp_info(output_file)
            print("</datasource_vtp>")
            output_file.write("</datasource_vtp>\r\n")
        elif curr_round == 3:
            print("<datasource_vlans>")
            output_file.write("<datasource_vlans>\r\n")
            devices_l[device_iterator].print_vlans(output_file)
            print("</datasource_vlans>")
            output_file.write("</datasource_vlans>\r\n")
        elif curr_round == 4:
            print("<datasource_cdp>")
            output_file.write("<datasource_cdp>\r\n")
            devices_l[device_iterator].print_cdp_det_output(output_file)
            print("</datasource_cdp>")
            output_file.write("</datasource_cdp>\r\n")

        device_iterator += 1
        if device_iterator >= len(devices_l):
            if( curr_round < MAX_ROUND ):
                curr_round += 1
                device_iterator = 0
            # endif
        # endif
    # endwhile

# Read devices informations (device name, device type, serial number, uplink, port settings, etc. )
# Read switch informations

def read_information_switch():
    logging.basicConfig(filename = general_device.DEBUG_LOGFILE, level=logging.DEBUG)
    global child
    child.delaybeforesend = 1
    child.delayafterread = 2
    child.timeout = COMMAND_TIMEOUT
    my_device = SwitchClass()
    current_prompt = ""
    is_switch = False
    print("->Start to read information from switch->")
    logging.info('->Start to read information from switch->')
    child.sendline('\x0d')
    current_prompt = ("%s%s" % (child.before,child.after))
    current_prompt = str.strip(current_prompt)
    # print( "Prompt>%s<" % str.strip(current_prompt))
    # Set the terminal length to 0
    __response = cmd('term leng 0')
    #child.sendline('term leng 0')
    #child.expect(CISCO_COMMAND_PROMPT, timeout=COMMAND_TIMEOUT)
    # time.sleep(5)
    # __response = "%s%s" % (child.before,child.after)
    print(__response)
    logging.info(__response)
    #
    # send enter
    #
    child.sendline('\x0d')
    # waiting for command prompt
    try:
        child.expect(CISCO_COMMAND_PROMPT, timeout=COMMAND_TIMEOUT)
        __response = ("%s"% (child.before))
        # child.expect(pexpect.EOF, timeout=COMMAND_TIMEOUT)
        #__response = child.read_nonblocking(1024, timeout=COMMAND_TIMEOUT)
        #print("<read_nonblocking>%s</readnonblocking>" % __response)
#        logging.info("<read_nonblocking>%s</readnonblocking>" % __response)
    except:
        print("Command timed out, nothing to do. Continue.") # nothing to-do
#        logging.info("Inventory timed out, nothing to do. Continue.")

    # print("<enter>%s<->%s</enter>" % (child.before,child.after))
    my_device.hostname = __response.splitlines()
    my_device.hostname = my_device.hostname[len(my_device.hostname)-1]
    my_device.hostname = my_device.hostname.strip()
    print("HOSTNAME:::::::::>%s<" % (my_device.hostname))
    #
    # read inventory
    #
    child.buffer = ""

    inventory_output = cmd('show inventory')

    # child.sendline('show inventory')
    # waiting for command prompt
    # print("Waiting for answer, please be patient!")
    # try:
    #     child.expect(pexpect.EOF, timeout=COMMAND_TIMEOUT)
    # except:
    #     print("Inventory timed out, nothing to do. Continue.") # nothing to-do

    # inventory_output = ("%s%s" % (child.before,child.after))

    # print("<inventory>%s</inventory>" % inventory_output)
    logging.info(inventory_output)
    print( inventory_output )

    # process with inventory output
    my_device.process_inventory(inventory_output)
    # my_device.print_inventory()


    print( known_switches )
    inventory_iterator = 0
    while inventory_iterator < len(my_device.model):
        switch_iterator = 0
        print(my_device.model)
        while switch_iterator < len(known_switches):
            #print("%s<->%s" % (my_device.model[inventory_iterator],known_switches[switch_iterator] ))
            if  my_device.model[inventory_iterator] in known_switches[switch_iterator]:
                print("It's a switch!!!!!")
                is_switch = True
                my_device.deviceFunction = DevFunct.LAN
                break
            #endif
            switch_iterator += 1
            # endwhile
        inventory_iterator += 1

    if( not is_switch ):
        print("It's not a switch!!!!!")
        return False
    #
    # read interface status from switch
    #
    interface_output = cmd('show int status')

    # child.buffer = ""
    # child.sendline('show int status')
    # print("Number of ports: ", len(my_device.ports))

    # try:
    #     child.expect(pexpect.EOF, timeout=COMMAND_TIMEOUT)
    # except:
    #     print("Timed out, nothing to do. Continue.") # nothing to-do
    #     logging.info("Timed out, nothing to do. Continue.")


    # interface_output = ("%s%s" % (child.before,child.after))
    # print(interface_output)
    logging.info(interface_output)
    my_device.process_show_interface( interface_output)

    # my_device.print_interface_params()

    #
    # read trunk informations from switch
    #
    child.buffer = ""

    vlan_output = cmd('show int trunk')

    # child.sendline('show int trunk')

    # try:
    #     child.expect(pexpect.EOF, timeout=COMMAND_TIMEOUT)
    # except:
    #     print("Timed out, nothing to do. Continue.") # nothing to-do

    # vlan_output = ("%s%s" % (child.before,child.after))
    # print(vlan_output)
    logging.info(vlan_output)
    my_device.process_trunk_output( vlan_output)

    #
    # READ LLDP information
    #

    lldp_output = cmd('show lldp neighbors')

    # child.buffer = ""
    # child.sendline('show lldp neighbors')

    # try:
    #     child.expect(pexpect.EOF, timeout=COMMAND_TIMEOUT)
    # except:
    #     print("Timed out, nothing to do. Continue.") # nothing to-do
    #     logging.info("Timed out, nothing to do. Continue.")

    # lldp_output = ("%s%s" % (child.before,child.after))
    # print(lldp_output)
    logging.info(lldp_output)
    my_device.process_lldp_output(lldp_output)
    #my_device.print_interface_params()

    #
    # READ CDP information
    #
    #
    cdp_output = cmd('show cdp neighbors')

    # child.sendline('show cdp neighbors')

    # try:
    #     child.expect(pexpect.EOF, timeout=COMMAND_TIMEOUT)
    # except:
    #     print("Timed out, nothing to do. Continue.") # nothing to-do
    #     logging.info("Timed out, nothing to do. Continue.")

    # cdp_output = ("%s%s" % (child.before,child.after))
    #print("##########################################")
    # print(cdp_output)
    logging.info(cdp_output)
    print("##########################################")
    my_device.process_cdp_output(cdp_output)
    print("##########################################")

    #
    # READ CDP details information
    #
    #
    cdp_det_output = cmd('show cdp neighbors detail')

    # child.sendline('show cdp neighbors detail')

    # try:
    #     child.expect(pexpect.EOF, timeout=COMMAND_TIMEOUT)
    # except:
    #     print("Timed out, nothing to do. Continue.") # nothing to-do
    #     logging.info("Timed out, nothing to do. Continue.")

    # cdp_det_output = ("%s%s" % (child.before,child.after))
    #print("##########################################")
    # print(cdp_output)
    logging.info(cdp_det_output)
    print("##########################################")
    my_device.process_cdp_det_output(cdp_det_output)
    print("##########################################")
    #
    # READ VLAN output
    #
    #

    vlan_output = cmd('show vlan brief')

    # child.sendline('show vlan brief')

    # try:
    #     child.expect(pexpect.EOF, timeout=COMMAND_TIMEOUT)
    # except:
    #     print("Timed out, nothing to do. Continue.") # nothing to-do
    #     logging.info("Timed out, nothing to do. Continue.")

    # vlan_output = ("%s%s" % (child.before,child.after))
    # print("##########################################")
    # logging.info("##########################################")

    # print(vlan_output)
    logging.info(vlan_output)

    # print("##########################################")
    logging.info("##########################################")

    my_device.process_show_vlan_brief(vlan_output)

    # print("##########################################")
    logging.info("##########################################")

    vtp_output = cmd('show vtp status')

    # child.buffer = ""
    # child.sendline('show vtp status')


    # try:
    #     child.expect(pexpect.EOF, timeout=COMMAND_TIMEOUT)
    # except:
    #     print("Timed out, nothing to do. Continue.") # nothing to-do
    #     logging.info("Timed out, nothing to do. Continue.")

    # vtp_output = ("%s%s" % (child.before,child.after))
    # print("##########################################")
    # logging.info("##########################################")

    # print(vlan_output)
    logging.info(vtp_output)

    # print("##########################################")
    logging.info("##########################################")

    my_device.process_show_vtp_status(vtp_output)

    # print("##########################################")
    logging.info("##########################################")

    # my_device.print_interface_params()

    #my_device.print_connections()
    #
    # READ power inline information
    # it may contain important info from AP's
    #
    devices_l.append(my_device)

    print("<-End read information from switch->")
    logging.info("<-End read information from switch->")
    return True

# Read router informations

def read_information_router():
    print("Please implement function read_information_router():!!!")
    return 0

# Read AP informations

def read_information_ap():
    print("Please implement function read_information_ap():!!!")
    return 0


def main():

    devices_list = []

# login to JUMPHOST, which is the first jump, constant JUMPHOST_IP
    spawn_args = "%s -l %s %s" % (SSH_COMMAND_ON_SERVER, USERNAME_JUMPHOST, JUMPHOST_IP)

    print('---')
    print(spawn_args)
    print('---')
    global child
    global output_file
    child = pexpect.spawn( spawn_args , timeout=JUMPHOST_CONN_TIMEOUT)
    child.delaybeforesend = 1.0
    # child = pexpect( SSH_COMMAND + '-l %s %s'%(USERNAME_JUMPHOST, JUMPHOST_IP))
    fout = open(general_device.DEVICE_OUTPUT_LOGFILE, "wb")
    # child.logfile = fout
    child.logfile=fout

    output_file = open(general_device.OUTPUT_FILE, "wb")

    is_switch = False
    #child.logfile_read = sys.stdout

    try:
        # Wait for
        child.expect('(?i)assword')
        # Wait for 'noecho' signal
        child.waitnoecho(WAIT_NOECHO)
        # Send password
        child.sendline(PASSWORD_JUMPHOST)
        # Wait for server prompt
        child.expect(SERVER_PROMPT, JUMPHOST_TIMEOUT)
        # Send custom command
        #child.sendline('df -h')
        #child.expect(SERVER_PROMPT)
        #print("--------------------->%s<->%s<---------" % (child.before,child.after))
        #time.sleep(0.1)
        # Wait for server prompt
        child.sendline('\x0d')
        child.expect(SERVER_PROMPT)

        add_prompt_to_stack( "%s%s" % (child.before, child.after))
        #mystring = str.strip(child.before)
        #print("--------------------->%s<---------" % (mystring))

    except pexpect.TIMEOUT:
        print ('Connection timed out to %s' % (JUMPHOST_IP) )
        sys.exit(1)
    except:
        print('Can not connect to %s' % (JUMPHOST_IP) )
        print(str(child))
        sys.exit(1)

    print('Successfully connected to %s server.' % (JUMPHOST_IP) )
    time.sleep(0.1)

# Login to the second jump host using constant JUMPHOST_IP_SWITCH and AAA user/pwd
# IF not connect, then exit with error msg
    conn_jump_args = "%s -l %s %s" % (SSH_COMMAND_ON_SERVER, USERNAME_AAA, JUMPHOST_IP_SWITCH)

    print('---')
    print(conn_jump_args)
    print('---')
    global child
    child.sendline( conn_jump_args )

    try:
        # Wait for
        child.expect('(?i)assword')
        # Wait for 'noecho' signal
        child.waitnoecho(WAIT_NOECHO)
        # Send password
        child.sendline(PASSWORD_AAA)
        # Wait for server prompt
        child.expect(CISCO_COMMAND_PROMPT, JUMPHOST_TIMEOUT)
        # Send custom command
        print("--------------------->%s<->%s<---------" % (child.before,child.after))
        time.sleep(0.1)
        # Wait for server prompt
        child.sendline('\x0d')
        child.expect(CISCO_COMMAND_PROMPT)

        add_prompt_to_stack( "%s%s" % (child.before, child.after))
        #mystring = str.strip(child.before)
        #print("--------------------->%s<---------" % (mystring))

    except pexpect.TIMEOUT:
        print ('Connection timed out to %s' % (JUMPHOST_IP_SWITCH) )
        sys.exit(1)
    except:
        print('Can not connect to %s' % (JUMPHOST_IP_SWITCH) )
        print(str(child))
        sys.exit(1)

    print('Successfully connected to %s server.' % (JUMPHOST_IP_SWITCH) )
    time.sleep(0.1)

    #ssh_con_ret = connect_with_ssh( JUMPHOST_IP_SWITCH, USERNAME_AAA, PASSWORD_AAA)

        ### active connection to server
        # Implement everything here if you want to use the first server as jump
        # START --->
    #print("login-stack->>>")
    #print_login_stack()
    #print("<<<-login-stack")
    #sys.exit(50)
# Loading devices from file, one ip address in one line
    try:
        with open(DEVICE_LIST_FILE, 'r') as fp:
                line = fp.readline()
                while line:
                    devices_list.append(str.strip(line))
                    line = fp.readline()
                    #    device_list_f = open(DEVICE_LIST_FILE, 'r')
                    #    device_lines = device_list_f.readlines()
                    #    for line in device_lines
        # Load filecontent to the list without newline char's
            #        devices_list.append(str.strip(line))
            # close the file
        fp.close()
    except IOError as e:
        print('Can not open the file %s : %s' % (DEVICE_LIST_FILE, e.strerror))
        #print(str(device_list_f))
        sys.exit(1)
    #sys.exit(0)

    # Go through on devices in a loop
    device_iterator = 0
    for list_item in devices_list:
        device_iterator = device_iterator + 1
        print('\"Read information from %s -> %s address\"' % (device_iterator, list_item))
            # If it a SWITCH
        child.sendline()
        ssh_con_ret = connect_with_ssh( list_item, USERNAME_AAA, PASSWORD_AAA)
        if ssh_con_ret == None:
           print('Connection to %s IP failed. Please make sure, it is available!' % list_item)
           continue

           time.sleep(0.1)
          # print('Successfully connected to %s' % list_item )
           child.sendline('exit')
        else:

            #is_switch = read_information_switch()
            #if is_switch:
            read_information_switch()
            print_information_switch()

            # endif
            # should quit to jumphost before connecting to another switch!!!!
            child.sendline('exit')
            child.expect(CISCO_COMMAND_PROMPT, SWITCH_CONN_TIMEOUT)
            print("%s%s" % (child.before,child.after))
                    # Try to login using SSH and AAA user/pw

                    # if it fail, then try to login using SSH and local/pw

                    # if it fail, then try to login using telnet and AAA user/pw

                    # if it fail, then try to login using telnet and local user/pw


            # If it is a ROUTER

                # Try to login using SSH and AAA user/pw

            # If it is an ACCESS POINT

                # Try to login using SSH and AAA user/pw

                # if it fail, then try to login using SSH and local user/pw



        #
        ### active connection to server
        # Implement everything here if you want to use the first server as jump
        #

        # Send 'exit' command to server
    child.sendline('exit')

    print_information_switch()

    output_file.close()
    sys.exit(0)
    '''
    try:
        i = child.expect([pexpect.TIMEOUT, SSH_NEWKEY, COMMAND_PROMPT, '(?)assword'])
        print( 'return value was :' + i )
    except pexpect.TIMEOUT:
        print ('Timed out')
        sys.exit (1)
    except:
        print('Unexpected exception at login to JUMPHOST')
        print(str(child))
        sys.exit (1)

    print( 'return value was :' + i )
    sys.exit(0)

    if i == 0: # Timeout
        print('ERROR! could not login with SSH. Here is what SSH said:')
        print(child.before, child.after)
        print(str(child))
        sys.exit (1)
    if i == 1: # In this case SSH does not have the public key cached.
        child.sendline ('yes')
        child.expect ('(?i)password:')
    if i == 2:
       # This may happen if a public key was setup to automatically login.
       # But beware, the COMMAND_PROMPT at this point is very trivial and
       # could be followed by some output in the MOTD or login message.
       pass
    if i == 3:
        child.sendline(PASSWORD_JUMPHOST)
        # Now we are either at the command prompt or
        # the login process is asking for our terminal type.
        i = child.expect ([COMMAND_PROMPT, TERMINAL_PROMPT])
        if i == 1:
            child.sendline (TERMINAL_TYPE)
            child.expect (COMMAND_PROMPT)


'''
    return 0


if __name__ == "__main__":
    main()
