#!/usr/bin/python
"""
@author Sung Kim, Minho Shim

CS 3251 Computer Network I
Programming Assignment 2
File Transfter Application (FxA)

FxA Server
"""

import time,readline,thread,threading
import sys,struct,fcntl,termios
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from rxp.rxp_socket import * # Import RxP Protocol
from fxa_utility import *

def clearCurrentReadline():
	# http://stackoverflow.com/questions/2082387/reading-input-from-raw-input-without-having-the-prompt-overwritten-by-other-th
	# Next line said to be reasonably portable for various Unixes
	(rows,cols) = struct.unpack('hh', fcntl.ioctl(sys.stdout, termios.TIOCGWINSZ,'1234'))

	text_len = len(readline.get_line_buffer())+2

	# ANSI escape sequences (All VT100 except ESC[0G)
	sys.stdout.write('\x1b[2K')						 # Clear current line
	sys.stdout.write('\x1b[1A\x1b[2K'*(text_len/cols))  # Move cursor up and clear line
	sys.stdout.write('\x1b[0G')						 # Move to start of line

def printCommandIndicater():
	""" Print user command again """ 
	last_line = readline.get_line_buffer()
	if last_line.endswith('\n'):
		sys.stdout.write('server command > ')
	else:
		sys.stdout.write('server command > ' + readline.get_line_buffer())
	sys.stdout.flush()

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
		threading.Thread.__init__(self, name=name)

	def run(self):
		""" Create socket """
		sock = Socket()
		# if sock < 0:
		# 	DieWithUserMessage('socket()', 'failed to create a socket')

		""" Bind to given port number """
		sock.bind(('', self._portNumber))
		# if (sock.bind(('', self._portNumber)) < 0):
		# 	DieWithUserMessage("bind()", "failed to bind to given port number")
		
		""" Clear terminal line """
		clearCurrentReadline()
		
		""" Mark the socket so it will listen for incoming connections """
		sock.listen()
		# if (sock.listen(self._MAXPENDING) < 0):
		# 	DieWithUserMessage("listen()", \
		# 		"failed to set socket to listen incoming connections")
		""" Wait for a client to connect """
		sock.accept()

		""" Print user command again """ 
		printCommandIndicater()

		""" Main Server Loop """
		while not self._stopevent.isSet():
			if sock.status == ConnectionStatus.NONE:
				break
			# if (clntSock < 0):
			# 	DieWithUserMessage("accept() failed", \
			# 		"socket failed to accept incoming connection")
			
			""" Clear terminal line """
			clearCurrentReadline()

			""" Handle accepted client """	
			clientThread = ClientHandlerThread(HandleFxAClient, self, sock)
			clientThread.start()
			clientThread.join()

			""" Print user command again """ 
			printCommandIndicater()

		""" When server is terminated by user command """
		runServer()

	def join(self, timeout=None):
		try:
			""" Stop the thread and wait for it to end. """
			sys.exit()
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

			print "fxa_server: Command received -> " + str(command) # DEBUG

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
runServer()
