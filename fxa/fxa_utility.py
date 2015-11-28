#!/usr/bin/python
"""
@author Sung Kim, Minho Shim

CS 3251 Computer Network I
Programming Assignment 2
File Transfter Application (FxA)

FxA Utility
	This utility functions work in both FxA server and client.
"""

import time,readline,thread,threading
import sys,struct,fcntl,termios
import os.path
# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from math import ceil

DATA_CHUNK_SIZE = 128000 # 128 kB

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

def DieWithUserMessage(msg, detail):
	""" Die with user message """
	print '\n' + msg + ': ' + detail + '\n'
	sys.exit()


def SendData(sock, dataToSend):
	""" Send data using socket """
	if dataToSend:
		# print "SendData(): sending data ->", str(dataToSend)[:40] # DEBUG
		bytesSent = sock.send(dataToSend)
		# print "SendData(): sent data successfully"# DEBUG
		# if (bytesSent < 0):
		# 	DieWithUserMessage("send()", "failed");
		# elif (sys.getsizeof(dataToSend) != bytesSent):
		# 	# check if bytes sent is the same with size of given data
		# 	DieWithUserMessage("send()", "sent unexpected number of bytes")
		return 0
	else:
		""" Clear terminal line """
		clearCurrentReadline()
		print "SendData(): nothing to send"
		""" Print user command again """ 
		printCommandIndicater()
		return 1

def ReceiveData(sock, blocking=False):
	""" Receive data using socket """
	# print "ReceiveData(): trying to receive data..." # DEBUG
	recvFlag, recvData = sock.recv(blocking=blocking)
	# print "ReceiveData(): received data ->", str(recvData)[:40] # DEBUG
	if recvFlag == True:
		return True, recvData
	# if (bytesReceived < 0):
	# 	DieWithUserMessage("recv()", "failed");
	# elif bytesReceived == 0:
	# 	return 1, None
	return False, ""


def HandleFxAClient(sock):
	""" 
		Handle FxA Client

		1. Receive Request (GET or POST)
		2. If GET is requested, send requested file. In case of POST,
		   be ready to received specified amount of data chunks

	"""

	# first recieved data would be request from client
	recvFlag, recvData = ReceiveData(sock, blocking=True)
	if (recvFlag != True):
		""" Clear terminal line """
		clearCurrentReadline()
		print "Disconnect: Connection " + str(sock.destAddr) + " Terminated."
		""" Print user command again """ 
		printCommandIndicater()
		sys.exit()
	request = str(recvData)
	command = request.split(':')
	if (len(command) != 2):
		DieWithUserMessage("HandleFxAClient()", "invalid request")
	elif (command[0].lower() == "get"):
		# When client request is GET request
		fileToSend = command[1]
		if not os.path.isfile(fileToSend):
			""" Clear terminal line """
			clearCurrentReadline()
			print "Such file '" + str(fileToSend) + "' doesn't exist"
		else:
			""" Clear terminal line """
			clearCurrentReadline()
			print "Sending " + fileToSend + "..."
			# Get file size and count number of data to send
			fileSize = os.path.getsize(fileToSend)
			# next recieved data would be number of data chunks to receive
			# receive as string and convert to integer
			numOfChunks = int(ceil(fileSize / float(DATA_CHUNK_SIZE)))
			# Send number of chunks first
			sendFlag = SendData(sock, str(numOfChunks))
			if (sendFlag != 0):
				DieWithUserMessage("SendData()", \
					"Program failed to send data properly")
			# Split file and send data
			with open(fileToSend, "rb") as f:
				for i in range(numOfChunks):
					# print "reading chunk no." + str(i) # DEBUG
					dataChunk = f.read(DATA_CHUNK_SIZE)
					if dataChunk:
						sendFlag = SendData(sock, dataChunk)
						if (sendFlag != 0):
							DieWithUserMessage("SendData()", \
								"Program failed to send data properly")
					else:
						DieWithUserMessage("HandleFxAClient() for GET request", \
							"Expected number of data chunks is different with actual data")
				f.close()
				""" Clear terminal line """
				clearCurrentReadline()
				print "Sent " + fileToSend + " successfully."
	elif (command[0].lower() == "post"):
		# When client request is POST request
		fileToGet = command[1]

		""" Clear terminal line """
		clearCurrentReadline()
		print "Receiving " + fileToGet + "..."

		# first recieved data would be number of data chunks to receive
		# receive as string and convert to integer
		recvFlag, recvData = ReceiveData(sock)
		if (recvFlag != True):
			DieWithUserMessage("ReceiveData()", \
				"unknown error")
		numOfChunks = int(recvData)

		directory = "server-received"
		if not os.path.exists(directory):
			os.makedirs(directory)

		# Write binary data to a file
		with open(directory + '/' + fileToGet, 'wb') as f:
			# received designated number of data chunks then write it
			for i in range(numOfChunks):
				recvFlag, recvData = ReceiveData(sock)
				if (recvFlag != True):
					DieWithUserMessage("ReceiveData()", \
						"unknown error")
				# recvData must be binary data. There's no check for this.
				f.seek(0, 2) # go to eof: relative position 0 from eof(2)
				f.write(recvData)
			f.close()
			""" Clear terminal line """
			clearCurrentReadline()
			print "Received " + fileToGet + " successfully."
	else:
		DieWithUserMessage("HandleFxAClient()", "unknown request")