'''
ezsshclient.py : This module provides a simple SSH client class that can connect
to a target device when instantiated, and execute a command when called
returning the output of the command.

Example Usage:

myrouter = ezsshclient.ezssh('10.192.255.11','admin','cisco.123')

>>> print(myrouter('show run int ethernet1/1'))

show run int ethernet1/1
!Command: show running-config interface Ethernet1/1
!Time: Wed Aug 20 17:24:31 2014
version 6.1(2)I2(2b)
interface Ethernet1/1
  description vPC Peer Link
  switchport
  switchport mode trunk
  channel-group 10 mode active
  no shutdown

NOTE:
This module requires the Paramiko module to be installed:  
https://pypi.python.org/pypi/paramiko/1.14.0
http://osxdaily.com/2012/07/10/how-to-install-paramiko-and-pycrypto-in-mac-os-x-the-easy-way/
'''

import paramiko
import time
import socket

class AllowAllKeys(paramiko.MissingHostKeyPolicy):
    def missing_host_key(self, client, hostname, key):
        return

class ConnectError(Exception):
    pass

class ezssh(object):
    def __init__(self):
        paramiko.util.log_to_file("logfile.log")
        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(AllowAllKeys())

    def __call__(self,command):
        '''
        command = string containing a command to send to the device
        '''
        self.remote.send('\n')
        time.sleep(1)
        prompt = self.remote.recv(1000).decode().strip()
        self.remote.send(command + '\n')
        time.sleep(2)
        data = ''
        while prompt not in data:           
           data = data + self.remote.recv(1000).decode()
                   
        return data

    def connect(self,host,userid,password):
        '''
        host =  string containing IP address or hostname of target device
        userid = string containing username to log into the target device
        password = string containing password to log into the target device
        '''
        try:
            self.client.connect(host,username=userid,password=password,timeout=10)      
        except paramiko.ssh_exception.AuthenticationException as e:
            raise ConnectError(e)
        except socket.error as e:
            raise ConnectError(e)
        except paramiko.SSHException as e:
            raise ConnectError(e)      
        self.remote = self.client.invoke_shell()
        incoming = self.remote.recv(4000)
        if ">" in incoming.decode():
            self.remote.send('en\n')
            incoming = self.remote.recv(4000)
            while ":" not in incoming.decode():
			    time.sleep(1)
			    incoming = self.remote.recv(4000)
            self.remote.send(password)
        self.remote.send('\n')
        self.remote.send('term len 0\n')
        time.sleep(2)
        incoming = self.remote.recv(4000)
		
    def isconnected(self):
        '''
        Method that returns true if the connection is active, false if not.
        '''
        if self.client.get_transport():
            return self.client.get_transport().is_active()
        else:
            return False          
  
    def disconnect(self):
        '''
        Use this to disconnect the session when complete
        '''
        self.client.close()