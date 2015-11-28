#!/usr/bin/python
"""
@author Sung Kim, Minho Shim

CS 3251 Computer Network I
Programming Assignment 2
File Transfter Application (FxA)

FxA Server
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from rxp.rxp_socket import * # Import RxP Protocol
from fxa_utility import *

class ClientHandlerThread(threading.Thread):
	def __init__(self, target, parentThread, *args):
		self._stopevent = threading.Event()
		self._target = target
		self._args = args
		self._parent = parentThread
		threading.Thread.__init__(self)
 
	def run(self):
		self._target(*self._args)

	def join(self, timeout=None):
		try:
			""" Stop the thread and wait for it to end. """
			self._stopevent.set()
			threading.Thread.join(self, timeout)
		except (KeyboardInterrupt, SystemExit):
			raise


class ServerThread(threading.Thread):
	_connected = False
	_MAXPENDING = 5 # Maximum outstanding connection requests

	# Python Cookbook, 2nd Edition; 9.2 Terminating a Thread
	# Credit: Doug Fort
	def __init__(self, port, netemuAddr, netemuPort, name='ServerThread'):
		""" constructor, setting initial variables """
		self._stopevent = threading.Event()
		self._sleepperiod = 1.0
		self._portNumber = port
		self._destAddress = netemuAddr, netemuPort
		self.sock = -1
		threading.Thread.__init__(self, name=name)

	def run(self):
		""" Create socket """
		self.sock = Socket()
		# if sock < 0:
		# 	DieWithUserMessage('socket()', 'failed to create a socket')

		""" Bind to given port number """
		self.sock.bind(('', self._portNumber))
		# if (sock.bind(('', self._portNumber)) < 0):
		# 	DieWithUserMessage("bind()", "failed to bind to given port number")
		
		
		
		""" Mark the socket so it will listen for incoming connections """
		self.sock.listen()
		
		# if (sock.listen(self._MAXPENDING) < 0):
		# 	DieWithUserMessage("listen()", \
		# 		"failed to set socket to listen incoming connections")
		""" Wait for a client to connect """
		acceptDestAddr = self.sock.accept()

		""" Clear terminal line """
		clearCurrentReadline()
		print "Connection established with client: " + str(acceptDestAddr)
		""" Print user command again """ 
		printCommandIndicater()

		""" Main Server Loop """
		while not self._stopevent.isSet():
			if self.sock.status == ConnectionStatus.NONE:
				break
			# if (clntSock < 0):
			# 	DieWithUserMessage("accept() failed", \
			# 		"socket failed to accept incoming connection")

			""" Handle accepted client """	
			clientThread = ClientHandlerThread(HandleFxAClient, self, self.sock)
			clientThread.start()
			clientThread.join()

		""" When server is terminated by user command """
		runServer()

	def join(self, timeout=None):
		try:
			""" Stop the thread and wait for it to end. """
			os._exit(1)
			self._stopevent.set()
			threading.Thread.join(self, timeout)
		except (KeyboardInterrupt, SystemExit):
			raise

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
def runServer():
	if __name__ == '__main__':
		portNumber = eval(sys.argv[1])
		netemuHost = sys.argv[2]
		netemuPort = eval(sys.argv[3])
		# Create Server Thread Object and execute it
		serverthread = ServerThread(portNumber, netemuHost, netemuPort)
		serverthread.start()
		""" Get user command from this point """
		# connection = False # connection is yet established
		while True:
			command = raw_input("server command > ")

			# print "fxa_server: Command received -> " + str(command) # DEBUG

			command = command.split(None) # split given string with whitespace

			if (len(command) < 1):
				continue

			if (command[0].lower() == "terminate"):
				""" Terminates gracefully from the FxA-server """
				# if (connection != True):
				# 	print "Establish connection before using this command."
				if (len(command) > 1):
					print "Wrong command: Try again."
				else: 
					serverthread.join() # terminate server thread and close server
					print "fxa_server exits..." # DEBUG
					sys.exit()

			elif (command[0].lower() == "window"):
				if (len(command) != 2):
					print "Wrong command: Try again."
				else:
					orgWindowSize = serverthread.sock.getWindowSize()
					newWindowSize = int(command[1])
					if serverthread.sock.setWindowSize(newWindowSize):
						print "Window size changed from", orgWindowSize, "to ->", newWindowSize
runServer()
