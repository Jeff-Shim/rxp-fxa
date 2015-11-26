#!/usr/bin/python
"""
@author Sung Kim, Minho Shim

CS 3251 Computer Network I
Programming Assignment 2
File Transfter Application (FxA)

FxA Server
"""

import time,readline,thread
import sys,struct,fcntl,termios
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import rxp_server

# import rxp.rxp_socket # Import RxP Protocol
from fxa_utility import *

class ClientHandlerThread(threading.Thread):
    def __init__(self, target, *args):
        self._target = target
        self._args = args
        threading.Thread.__init__(self)
 
    def run(self):
        self._target(*self._args)


class ServerThread(threading.Thread):
	_connected = False
	_portNumber = None
	_netemuAddress = None
	_netemuPort = None
	_MAXPENDING = 5 # Maximum outstanding connection requests

	# Python Cookbook, 2nd Edition; 9.2 Terminating a Thread
	# Credit: Doug Fort
	def __init__(self, port, netemuAddr, netemuPort, name='ServerThread'):
		""" constructor, setting initial variables """
		self._stopevent = threading.Event()
		self._sleepperiod = 1.0
		self._portNumber = port
		self._netemuAddress = netemuAddr
		self._netemuPort = netemuPort
		threading.Thread.__init__(self, name=name)

	def run(self):
		""" Create socket """
		sock = socket()
		if sock < 0:
			DieWithUserMessage('socket()', 'failed to create a socket')
				
		""" Convert given string address into network address """
		rtnVal, networkAddr = sock.inet_pton(self._netemuAddress)
		if (rtnVal == 0):
			DieWithUserMessage("inet_pton() failed", "invalid address string")
		elif (rtnVal < 0):
			DieWithUserMessage("inet_pton() failed", "failed to convert address")
		networkPort = sock.htons(self._netemuPort)

		""" Bind to given port number """
		if (sock.bind(self_portNumber) < 0):
			DieWithUserMessage("bind()", "failed to bind to given port number")

		""" Mark the socket so it will listen for incoming connections """
		if (sock.listen(self._MAXPENDING) < 0):
			DieWithUserMessage("listen()", \
				"failed to set socket to listen incoming connections")

		""" Main Server Loop """
		while not self._stopevent.isSet():
			clntAddr = None
			""" Wait for a client to connect """
			clntSock, clntAddr = sock.accept()
			if (clntSock < 0):
				DieWithUserMessage("accept() failed", \
					"socket failed to accept incoming connection")

			""" Handle accepted client """	
			ClientHandlerThread(HandleFxAClient, clntSock).start()

		""" When server is terminated by user command """
		print "%s ends" % (self.getName(),)

	def join(self, timeout=None):
		""" Stop the thread and wait for it to end. """
		self._stopevent.set()
		threading.Thread.join(self, timeout)

	def setConnected(self, value):
		self._connected = value

	def isConnected(self):
		return self._connected

# Check number of arguments
if len(sys.argv) != 4:
	DieWithUserMessage('Command-line Error', 'fxa-sever X A P\n\n' \
		+ 'X: the port number at which the FxA-server\'s UDP socket' \
		+ ' should bind to (ddd number).\n' \
		+ 'A: the IP address of NetEmu\n' \
		+ 'P: the UDP port number of NetEmu')


if __name__ == '__main__':
	portNumber = sys.argv[1]
	netemuAddress = sys.argv[2]
	netemuPort = sys.argv[3]
	# Create Server Thread Object and execute it
	serverthread = ServerThread(portNumber, netemuAddress, etemuPort)
	serverthread.start()
	""" Get user command from this point """
	# connection = False # connection is yet established
	while True:
		command = raw_input("server command > ")
		command = command.split(None) # split given string with whitespace

		if (command[0].lower() == "terminate"):
			""" Terminates gracefully from the FxA-server """
			# if (connection != True):
			# 	print "Establish connection before using this command."
			if (len(command) > 1):
				print "Wront command: Try again."
			serverthread.join() # terminate server thread and close server
			sys.exit()
