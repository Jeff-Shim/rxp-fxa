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

DATA_CHUNK_SIZE = 500

def clearCurrentReadline():
	# http://stackoverflow.com/questions/2082387/reading-input-from-raw-input-without-having-the-prompt-overwritten-by-other-th
	# Next line said to be reasonably portable for various Unixes
	(rows,cols) = struct.unpack('hh', fcntl.ioctl(sys.stdout, termios.TIOCGWINSZ,'1234'))

	text_len = len(readline.get_line_buffer())+2

	# ANSI escape sequences (All VT100 except ESC[0G)
	sys.stdout.write('\x1b[2K')						 # Clear current line
	sys.stdout.write('\x1b[1A\x1b[2K'*(text_len/cols))  # Move cursor up and clear line
	sys.stdout.write('\x1b[0G')						 # Move to start of line


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
		threading.Thread.__init__(self, name=name)
		self._portNumber = port
		self._netemuAddress = netemuAddr
		self._netemuPort = netemuPort


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
			HandleFxAClient(clntSock)

			clearCurrentReadline()
			sys.stdout.write('> ' + readline.get_line_buffer())
			sys.stdout.flush()
			self._stopevent.wait(self._sleepperiod)
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
	connection = False # connection is yet established
	while True:
		command = raw_input("Type command and press enter: ")
		command = command.split(None) # split given string with whitespace

		if (command[0].lower() == "terminate"):
			""" Terminates gracefully from the FxA-server """
			if (connection != True):
				print "Establish connection before using this command."
			elif (len(command) > 1):
				print "Wront command: Try again."
			serverthread.join() # terminate server thread and close server
			sys.exit()
