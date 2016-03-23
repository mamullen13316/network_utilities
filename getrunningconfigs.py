'''
getrunningconfigs.py 1.0

This program will connect to a list of ip addresses/hostnames specified as user input, or via a .CSV file,
and collect the running configuration.  The output will be printed to stdout and also saved
to an individual text file for each device in the format hostname.txt. The output files will be saved in a new directory
which will be dynamically created in the current working directory.

Usage:

python getoutput.py [-p] [password] [-u] [userid] [-c] [commands] [-d] [devicefile.csv]

optional arguments:
  -h, --help            show this help message and exit
  -username USERNAME    Specify the username to log into the devices.  If omitted, program will prompt for username.
  -password PASSWORD    Specify the password to log into the devices.  If omitted, program will prompt for password.
  -devicefile DEVICEFILE
                        A file containing a list of IP addresses or hostnames, one per line.
  -command-list COMMAND_LIST
                        A command or list of commands separated by a semi-colon ;

Please see the README for installation and usage details.

REQUIREMENTS:

The program requires the Paramiko module to be installed:  
https://pypi.python.org/pypi/paramiko/1.14.0
http://osxdaily.com/2012/07/10/how-to-install-paramiko-and-pycrypto-in-mac-os-x-the-easy-way/

PyCrypto also needs to be installed as pre-requisite to Paramiko.  Both PyCrypto can be installed from the command line
using PIP:

pip install pycrypto
pip install paramiko

Additionally,  the ezsshclient.py module must be placed in the working directory with getoutput.py.
'''
import argparse
import os
import sys
import ezsshclient
import getpass
from datetime import datetime
import time

def zeropad_datetime(datetime_obj):
    '''Take a datetime object apart and zero pad each element'''
    yr = str(datetime_obj.year)
    mo = str(datetime_obj.month).zfill(2)
    dy = str(datetime_obj.day).zfill(2)
    hr = str(datetime_obj.hour).zfill(2)
    mn = str(datetime_obj.minute).zfill(2)
    sc = str(datetime_obj.second).zfill(2)
    return yr,mo,dy,hr,mn,sc

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='''getoutput.py -- Version 1.0 --
    This program will connect using SSH to a Cisco device specified on the command line,
    or alternatively a list of devices in a .csv file, and collect the output of a specified command
    or list of commands.  The output will be saved
    to an individual text file for each device in the format hostname.txt in a new directory
    that will be created in the current working directory.''')
    parser.add_argument('-username',help='A .CSV file containing a list of IP addresses or hostnames',required=False)
    parser.add_argument('-password',help='Specify the username to log into the devices.  If omitted, program will prompt for username.',required=False)
    parser.add_argument('-devicefile',help='A file containing a list of IP addresses or hostnames, one per line.',required=False)

    args = parser.parse_args()

    if args.devicefile:
        try:
            with open(args.devicefile,"r") as f:
                    if os.name == 'posix':
                        devicelist = [device.strip() for device in f.readlines()]
                    else:
                        devicelist = f.readlines()
        except:
            print("ERROR: Unable to open {0}".format(args.devicefile))
            quit()
    else:
        device= raw_input("Enter IP/Hostname: ")
        devicelist = [element.strip(' ') for element in device.split(',')]

    if args.username:
        USERID = args.username
    else:
        USERID = raw_input("Username: ")
    
    if args.password:
        PASSWORD = args.password
    else:
        PASSWORD = getpass.getpass()

    output_dict = {}
    result_dict = {}    
    
    for host in devicelist:
        host = host.rstrip('\n')
        if not host:
            continue
        print ("Connecting to {0}...".format(host))
        target = ezsshclient.ezssh()
        try:
            target.connect(host,USERID,PASSWORD)
            connect_success = True
            result_dict[host] = 'success'        
        except Exception as e:
            print ('Error connecting to {}: {}'.format(host,e))
            connect_success = False
            result_dict[host] = 'failed'
            continue

        if target.isconnected():
            print ('Successfully connected to {}!'.format(host))
            print ('Running commands...')
            
        '''Run each command on the device and return the output'''
        hostname =  str("".join(c for c in target('') if c not in '\r\n#> '))
        output_list = []
        output_list.append('-'*25 + hostname + '-'*25)
        output = target('show running')
        output_list.append(output)
        
        '''Print to stdout'''
        for line in output_list:
            print(line)
                
        ofile = hostname + '.txt'
        
        output_dict[hostname] = (ofile,output_list)

        target.disconnect()
        
    print('\n' + '*'*25 + 'SCRIPT RESULTS' + '*'*25 + '\n')
        
    for host in result_dict.keys():
        print ('{}: {}'.format(host,result_dict[host]))
    print ('\n')
    
    if connect_success:
        print('Writing output...')
        yr,mo,dy,hr,mn,sc = zeropad_datetime(datetime.now())
        outputdir = 'getrunningconfigs-{}{}{}{}{}{}'.format(mo,dy,yr,hr,mn,sc)
        os.mkdir(outputdir)
        for host in output_dict.keys(): 
            ofile = output_dict[host][0]
            output_list = output_dict[host][1]            
            outputfile = open(os.path.join(os.getcwd(),outputdir,ofile),"w")
            for item in output_list:
                outputfile.write(item + '\n') 
            outputfile.close()
            print ("\nOutput for {0} written to {1}".format(host,os.path.join(os.getcwd(),outputdir,ofile)))
            
    print ('\nFinished!')
    



    

